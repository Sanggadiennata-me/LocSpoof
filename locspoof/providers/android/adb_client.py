"""
Safe ADB (Android Debug Bridge) Client Wrapper.
Executes all commands via safe argument lists without shell interpretation.
Detects connected physical devices and emulators, injects GPS coordinates,
and queries the real reported location from Android LocationManagerService.
"""

import re
import time
from typing import Dict, List, Optional
from pydantic import BaseModel

from locspoof.core.exceptions import DependencyMissingError, DeviceNotFoundError, LocSpoofError
from locspoof.core.models import Coordinates
from locspoof.utils.logger import logger
from locspoof.utils.process import find_executable, safe_run


class AndroidDevice(BaseModel):
    serial: str
    state: str
    is_emulator: bool
    model: Optional[str] = None
    product: Optional[str] = None
    android_version: Optional[str] = None
    sdk_version: Optional[int] = None
    mock_location_status: Optional[str] = None


class AdbClient:
    """
    Hardened wrapper for the Android Debug Bridge (ADB).
    """

    def __init__(self, adb_path: Optional[str] = None):
        self.adb_path = adb_path or find_executable("adb")

    def is_available(self) -> bool:
        """Verify ADB binary is reachable in the system PATH."""
        return self.adb_path is not None

    def _ensure_available(self) -> None:
        if not self.is_available():
            raise DependencyMissingError(
                message="Android Debug Bridge (adb) binary not found.",
                detail="The 'adb' command was not located in your PATH.",
                suggestion="Install Android SDK Platform-Tools ('sudo apt install adb' or download from developer.android.com).",
            )

    def list_devices(self) -> List[AndroidDevice]:
        """
        List all connected devices and emulators via `adb devices -l`
        and query basic device attributes.
        """
        self._ensure_available()
        res = safe_run([self.adb_path, "devices", "-l"], timeout=8.0)
        if not res.success:
            raise LocSpoofError(
                message="Failed to query ADB devices.",
                detail=res.stderr or res.stdout,
                suggestion="Make sure the ADB server is running with 'adb start-server'.",
            )

        devices: List[AndroidDevice] = []
        lines = res.stdout.splitlines()
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                is_emu = serial.startswith("emulator-") or "emulator" in serial.lower()

                model = None
                product = None
                for token in parts[2:]:
                    if token.startswith("model:"):
                        model = token.split(":", 1)[1]
                    elif token.startswith("product:"):
                        product = token.split(":", 1)[1]

                # If device is authorized, query android version
                and_ver = None
                sdk_ver = None
                mock_status = "Available (Emulator GNSS)" if is_emu else "Requires Developer Options Mock App"

                if state == "device":
                    prop_res = safe_run(
                        [self.adb_path, "-s", serial, "shell", "getprop", "ro.build.version.release"],
                        timeout=3.0,
                    )
                    if prop_res.success and prop_res.stdout:
                        and_ver = prop_res.stdout.strip()

                    sdk_res = safe_run(
                        [self.adb_path, "-s", serial, "shell", "getprop", "ro.build.version.sdk"],
                        timeout=3.0,
                    )
                    if sdk_res.success and sdk_res.stdout.isdigit():
                        sdk_ver = int(sdk_res.stdout.strip())

                devices.append(
                    AndroidDevice(
                        serial=serial,
                        state=state,
                        is_emulator=is_emu,
                        model=model,
                        product=product,
                        android_version=and_ver,
                        sdk_version=sdk_ver,
                        mock_location_status=mock_status,
                    )
                )
        return devices

    def set_emulator_geo_fix(
        self,
        serial: str,
        latitude: float,
        longitude: float,
        altitude: Optional[float] = None,
    ) -> None:
        """
        Inject coordinates into Android Emulator using `adb -s <serial> emu geo fix <lon> <lat> [alt]`.
        Note: Android Emulator command requires Longitude FIRST, then Latitude.
        """
        self._ensure_available()
        cmd = [self.adb_path, "-s", serial, "emu", "geo", "fix", str(longitude), str(latitude)]
        if altitude is not None:
            cmd.append(str(altitude))

        logger.debug(f"Running safe ADB emu command: {' '.join(cmd)}")
        res = safe_run(cmd, timeout=8.0)
        if not res.success or "error" in res.stderr.lower() or "ko" in res.stdout.lower():
            err_msg = res.stderr or res.stdout
            raise LocSpoofError(
                message=f"Failed to set geo fix on emulator '{serial}'.",
                detail=err_msg,
                suggestion="Verify the emulator console auth token and ensure the emulator is unlocked.",
            )

    def set_test_provider_location(
        self,
        serial: str,
        latitude: float,
        longitude: float,
        altitude: Optional[float] = None,
        accuracy: float = 5.0,
    ) -> bool:
        """
        Inject mock location on physical device / modern Android using shell cmd location.
        Supported on Android 12+ (API 31+).
        """
        self._ensure_available()
        # 1. Grant MOCK_LOCATION to shell (UID 2000 and package com.android.shell)
        safe_run([self.adb_path, "-s", serial, "shell", "appops", "set", "2000", "android:mock_location", "allow"], timeout=4.0)
        safe_run([self.adb_path, "-s", serial, "shell", "appops", "set", "com.android.shell", "android:mock_location", "allow"], timeout=4.0)

        success = False
        for provider in ("gps", "fused"):
            # Syntax A (Android 14/15/16 with 'providers' subcommand)
            safe_run([self.adb_path, "-s", serial, "shell", "cmd", "location", "providers", "add-test-provider", provider], timeout=4.0)
            safe_run([self.adb_path, "-s", serial, "shell", "cmd", "location", "providers", "set-test-provider-enabled", provider, "true"], timeout=4.0)
            cmd_a = [
                self.adb_path, "-s", serial, "shell", "cmd", "location", "providers",
                "set-test-provider-location", provider,
                "--location", f"{latitude},{longitude}",
                "--accuracy", str(accuracy),
            ]
            res_a = safe_run(cmd_a, timeout=4.0)

            # Syntax B (Android 12/13 legacy without 'providers' subcommand)
            if not res_a.success:
                safe_run([self.adb_path, "-s", serial, "shell", "cmd", "location", "add-test-provider", provider], timeout=4.0)
                safe_run([self.adb_path, "-s", serial, "shell", "cmd", "location", "set-test-provider-enabled", provider, "true"], timeout=4.0)
                cmd_b = [
                    self.adb_path, "-s", serial, "shell", "cmd", "location",
                    "set-test-provider-location", provider,
                    "-a", str(accuracy),
                    str(latitude), str(longitude),
                ]
                res_b = safe_run(cmd_b, timeout=4.0)
                if res_b.success:
                    success = True
            else:
                success = True

        return success

    def get_reported_location(self, serial: str) -> Optional[Coordinates]:
        """
        Query the actual current reported location of the Android device
        from LocationManagerService dumpsys.
        """
        self._ensure_available()
        # 1. Try Android 12+ cmd location get-last-location
        cmd_res = safe_run(
            [self.adb_path, "-s", serial, "shell", "cmd", "location", "get-last-location", "gps"],
            timeout=4.0,
        )
        if cmd_res.success and cmd_res.stdout:
            coords = self._extract_coords_from_dump(cmd_res.stdout)
            if coords:
                return coords

        # 2. Fallback to dumpsys location
        dump_res = safe_run(
            [self.adb_path, "-s", serial, "shell", "dumpsys", "location"],
            timeout=6.0,
        )
        if dump_res.success and dump_res.stdout:
            return self._extract_coords_from_dump(dump_res.stdout)

        return None

    def _extract_coords_from_dump(self, text: str) -> Optional[Coordinates]:
        """
        Regex extraction for standard LocationManager Location[provider lat,lon ...] string.
        Examples:
          Location[gps 55.554250,55.765611 hAcc=15 ...]
          Location[fused -6.208800,106.845600 ...]
          last location=55.554250, 55.765611
        """
        # Pattern 1: Location[provider lat,lon ...]
        p1 = re.search(r"Location\[[a-zA-Z0-9_-]+\s+([+-]?\d+(?:\.\d+)?)[,\s]+([+-]?\d+(?:\.\d+)?)", text)
        if p1:
            try:
                lat = float(p1.group(1))
                lon = float(p1.group(2))
                return Coordinates(latitude=lat, longitude=lon)
            except Exception:
                pass

        # Pattern 2: (lat, lon) coordinates in dump
        p2 = re.search(r"(?:last\s+location|last\s+gps|last_location)[=:\s]+([+-]?\d+(?:\.\d+)?)[,\s]+([+-]?\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if p2:
            try:
                lat = float(p2.group(1))
                lon = float(p2.group(2))
                return Coordinates(latitude=lat, longitude=lon)
            except Exception:
                pass

        return None

    def stop_mock_location(self, serial: str, is_emulator: bool = True) -> None:
        """
        Disable mock providers and clear test locations.
        """
        self._ensure_available()
        if is_emulator:
            # Setting to 0,0 or null position
            safe_run([self.adb_path, "-s", serial, "emu", "geo", "fix", "0.0", "0.0"], timeout=6.0)
        else:
            for provider in ("gps", "fused", "network"):
                # Disable test provider (Android 14+ and legacy syntax)
                safe_run(
                    [self.adb_path, "-s", serial, "shell", "cmd", "location", "providers", "set-test-provider-enabled", provider, "false"],
                    timeout=4.0,
                )
                safe_run(
                    [self.adb_path, "-s", serial, "shell", "cmd", "location", "set-test-provider-enabled", provider, "false"],
                    timeout=4.0,
                )
                # Remove test provider so system provider takes back over
                safe_run(
                    [self.adb_path, "-s", serial, "shell", "cmd", "location", "providers", "remove-test-provider", provider],
                    timeout=4.0,
                )
                safe_run(
                    [self.adb_path, "-s", serial, "shell", "cmd", "location", "remove-test-provider", provider],
                    timeout=4.0,
                )
