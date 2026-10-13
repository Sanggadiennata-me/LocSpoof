"""
Android Device Location Provider for locspoof.
Core provider responsible for device-level GPS and LocationManager spoofing.
Supports Android Emulators and physical devices, verifies real reported device location,
and provides live periodic spoofing.
"""

import threading
import time
from typing import Dict, List, Optional

from locspoof.core.exceptions import DeviceNotFoundError, LocSpoofError
from locspoof.core.models import (
    Coordinates,
    Location,
    LocationSignal,
    LocationSource,
    OperationResult,
    ProviderCapability,
)
from locspoof.providers.android.adb_client import AdbClient, AndroidDevice
from locspoof.providers.base import BaseProvider
from locspoof.utils.logger import logger


class AndroidProvider(BaseProvider):
    """
    Core Android Mock Location and Emulator GPS Provider.
    """

    def __init__(self, adb_client: Optional[AdbClient] = None, preferred_serial: Optional[str] = None):
        self.adb = adb_client or AdbClient()
        self.preferred_serial = preferred_serial
        self._target_coords: Optional[Coordinates] = None
        self._live_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_spoofing_active = False

    @property
    def name(self) -> str:
        return "android"

    @property
    def description(self) -> str:
        return "Android Device & Emulator Mock Location Provider"

    def get_devices(self) -> List[AndroidDevice]:
        if not self.adb.is_available():
            return []
        try:
            return self.adb.list_devices()
        except Exception:
            return []

    def get_target_device(self) -> Optional[AndroidDevice]:
        devices = self.get_devices()
        if not devices:
            return None
        if self.preferred_serial:
            for d in devices:
                if d.serial == self.preferred_serial:
                    return d
        # Preference: active emulator first, otherwise active physical device
        emulators = [d for d in devices if d.is_emulator and d.state == "device"]
        if emulators:
            return emulators[0]
        active_devices = [d for d in devices if d.state == "device"]
        return active_devices[0] if active_devices else devices[0]

    def check_capability(self) -> ProviderCapability:
        if not self.adb.is_available():
            return ProviderCapability(
                name=self.name,
                available=False,
                status_summary="ADB NOT FOUND",
                suggestion="Install ADB (Android SDK Platform-Tools) and add it to your PATH.",
            )

        devices = self.get_devices()
        if not devices:
            return ProviderCapability(
                name=self.name,
                available=False,
                status_summary="NO DEVICES CONNECTED",
                suggestion="Launch an Android Emulator or connect an Android device with USB Debugging enabled.",
            )

        target = self.get_target_device()
        if target:
            device_type = "Android Emulator" if target.is_emulator else "Physical Device"
            model_str = f" ({target.model})" if target.model else ""
            summary = f"READY [{device_type}: {target.serial}{model_str}]"
            return ProviderCapability(
                name=self.name,
                available=True,
                status_summary=summary,
                details={
                    "serial": target.serial,
                    "state": target.state,
                    "is_emulator": target.is_emulator,
                    "model": target.model,
                    "android_version": target.android_version,
                    "sdk_version": target.sdk_version,
                    "mock_location_status": target.mock_location_status,
                },
            )

        return ProviderCapability(
            name=self.name,
            available=False,
            status_summary="OFFLINE",
            suggestion="Authorize USB debugging on the Android device screen.",
        )

    def apply_location(self, location: Location) -> OperationResult:
        """
        Apply simulated coordinates to Android device.
        """
        if not self.adb.is_available():
            return OperationResult(
                success=False,
                message="ADB binary not found in PATH.",
                error="DependencyMissing",
            )

        target = self.get_target_device()
        if not target:
            return OperationResult(
                success=False,
                message=(
                    "No Android device or emulator currently connected.\n\n"
                    "Suggestion: Connect an Android phone via USB with Debugging enabled, "
                    "or start an emulator with 'emulator @<avd_name> &'.\n"
                    "Check connected devices with 'locspoof devices'."
                ),
                error="DeviceNotFound",
            )

        self._target_coords = location.coordinates

        # 1. Target is an Android Emulator
        if target.is_emulator:
            try:
                self.adb.set_emulator_geo_fix(
                    serial=target.serial,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    altitude=location.altitude,
                )
                self._is_spoofing_active = True

                # Verify what location device is reporting
                reported = self.adb.get_reported_location(target.serial)

                details = {
                    "device": target.serial,
                    "type": "Android Emulator",
                    "target": f"{location.latitude}, {location.longitude}",
                    "reported": f"{reported.latitude}, {reported.longitude}" if reported else "Awaiting first fix",
                    "status": "ACTIVE",
                }

                return OperationResult(
                    success=True,
                    message=f"Injected GPS location into emulator '{target.serial}' ({location.latitude}, {location.longitude}).",
                    details=details,
                )
            except Exception as exc:
                return OperationResult(
                    success=False,
                    message=f"Failed to set geo fix on emulator: {exc}",
                    error=str(exc),
                )

        # 2. Target is a Physical Android Device
        else:
            try:
                # Attempt Android 12+ shell test provider injection
                applied = self.adb.set_test_provider_location(
                    serial=target.serial,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    altitude=location.altitude,
                )
                if applied:
                    self._is_spoofing_active = True
                    reported = self.adb.get_reported_location(target.serial)
                    details = {
                        "device": target.serial,
                        "type": "Physical Android Device",
                        "target": f"{location.latitude}, {location.longitude}",
                        "reported": f"{reported.latitude}, {reported.longitude}" if reported else "Applied via TestProvider",
                        "status": "ACTIVE",
                    }
                    return OperationResult(
                        success=True,
                        message=f"Applied test provider mock location to physical device '{target.serial}'.",
                        details=details,
                    )
                else:
                    return OperationResult(
                        success=False,
                        message=(
                            f"Device '{target.serial}' is a physical phone. "
                            "Please select a Mock Location App in Developer Options "
                            "(Settings -> Developer options -> Select mock location app)."
                        ),
                        details={"device": target.serial, "is_emulator": False},
                    )
            except Exception as exc:
                return OperationResult(
                    success=False,
                    message=f"Error applying mock location to physical device: {exc}",
                    error=str(exc),
                )

    def start_live_spoofing(self, location: Location, interval: float = 1.0) -> None:
        """
        Maintain continuous mock location updates so Android apps do not expire the fix.
        """
        self.apply_location(location)
        self._stop_event.clear()

        def _worker():
            target = self.get_target_device()
            while not self._stop_event.is_set():
                if target and self._target_coords:
                    try:
                        if target.is_emulator:
                            self.adb.set_emulator_geo_fix(
                                serial=target.serial,
                                latitude=self._target_coords.latitude,
                                longitude=self._target_coords.longitude,
                                altitude=self._target_coords.altitude,
                            )
                        else:
                            self.adb.set_test_provider_location(
                                serial=target.serial,
                                latitude=self._target_coords.latitude,
                                longitude=self._target_coords.longitude,
                            )
                    except Exception:
                        pass
                time.sleep(interval)

        self._live_thread = threading.Thread(target=_worker, daemon=True)
        self._live_thread.start()

    def stop_live_spoofing(self) -> None:
        self._stop_event.set()
        if self._live_thread and self._live_thread.is_alive():
            self._live_thread.join(timeout=1.0)
        self._is_spoofing_active = False

    def get_current_signal(self) -> LocationSignal:
        target = self.get_target_device()
        cap = self.check_capability()
        reported_coords = None
        if target and self.adb.is_available():
            try:
                reported_coords = self.adb.get_reported_location(target.serial)
            except Exception:
                pass

        active_coords = reported_coords or self._target_coords

        return LocationSignal(
            source=LocationSource.EMULATOR if (target and target.is_emulator) else LocationSource.ANDROID,
            source_name=f"Android ({target.serial if target else 'No Device'})",
            coordinates=active_coords,
            is_active=cap.available and self._is_spoofing_active,
            raw_details={
                "target_coords": self._target_coords.model_dump() if self._target_coords else None,
                "reported_coords": reported_coords.model_dump() if reported_coords else None,
                "spoofing_active": self._is_spoofing_active,
            },
            error_message=None if cap.available else cap.status_summary,
        )

    def reset(self) -> OperationResult:
        self.stop_live_spoofing()
        target = self.get_target_device()
        if target and self.adb.is_available():
            try:
                self.adb.stop_mock_location(target.serial, is_emulator=target.is_emulator)
            except Exception:
                pass
        self._target_coords = None
        self._is_spoofing_active = False
        return OperationResult(success=True, message="Android device mock location reset successfully.")
