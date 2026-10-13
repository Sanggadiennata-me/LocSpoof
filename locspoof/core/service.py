"""
Core Location Service orchestrator for locspoof.
Refocused on Device-Level Location Spoofing as the primary capability,
with Coordinate Parsing, ADB Mock Location control, and real-time status verification.
"""

from typing import Dict, List, Optional, Tuple

from locspoof.config.settings import Config
from locspoof.config.storage import load_config, save_config
from locspoof.core.coordinate_parser import parse_coordinates
from locspoof.core.exceptions import LocSpoofError, ValidationError
from locspoof.core.geocoder import Geocoder
from locspoof.core.models import (
    Coordinates,
    Location,
    LocationSignal,
    LocationSource,
    LocationVerification,
    OperationResult,
)
from locspoof.providers.android.adb_client import AndroidDevice
from locspoof.providers.android.provider import AndroidProvider
from locspoof.providers.manager import ProviderManager
from locspoof.verification.engine import VerificationEngine


class LocationService:
    """
    Central service orchestrating locspoof operations with priority on Android Device Location Spoofing.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        provider_manager: Optional[ProviderManager] = None,
        geocoder: Optional[Geocoder] = None,
        verification_engine: Optional[VerificationEngine] = None,
    ):
        self.config = config or load_config()
        self.provider_manager = provider_manager or ProviderManager()
        self.geocoder = geocoder or Geocoder()
        self.verification_engine = verification_engine or VerificationEngine(
            distance_threshold_km=self.config.verification.distance_threshold_km
        )

    @property
    def android_provider(self) -> AndroidProvider:
        p = self.provider_manager.get_provider("android")
        if isinstance(p, AndroidProvider):
            return p
        return AndroidProvider()

    def list_devices(self) -> List[AndroidDevice]:
        """List attached Android devices and emulators with detailed capabilities."""
        return self.android_provider.get_devices()

    def spoof_device_location(
        self,
        coord_input: str,
        device_id: Optional[str] = None,
    ) -> Tuple[Location, OperationResult, Optional[Coordinates]]:
        """
        Primary execution entrypoint:
        1. Parse coordinate (DMS or Decimal)
        2. Set target device location via Android Provider
        3. Verify reported device location
        """
        # 1. Parse coordinate using the robust multi-format parser
        coords = parse_coordinates(coord_input)

        loc = Location(
            latitude=coords.latitude,
            longitude=coords.longitude,
            source=LocationSource.ANDROID,
        )

        # 2. Configure provider preference
        if device_id:
            self.android_provider.preferred_serial = device_id
            self.config.android.preferred_device = device_id

        # 3. Apply location to Android device
        res = self.android_provider.apply_location(loc)

        # 4. Save state to configuration
        self.config.active_location = loc
        save_config(self.config)

        # 5. Query verified reported location from device
        target_device = self.android_provider.get_target_device()
        reported_coords = None
        if target_device and self.android_provider.adb.is_available():
            try:
                reported_coords = self.android_provider.adb.get_reported_location(target_device.serial)
            except Exception:
                pass

        return loc, res, reported_coords

    def stop_spoofing(self, device_id: Optional[str] = None) -> OperationResult:
        """
        Stop mock location and restore normal device location.
        """
        if device_id:
            self.android_provider.preferred_serial = device_id
        res = self.android_provider.reset()
        self.config.active_location = None
        save_config(self.config)
        return res

    def get_spoof_status(self) -> Dict:
        """
        Gather current device spoofing status, target coordinates, and verified reported coordinates.
        """
        target_device = self.android_provider.get_target_device()
        cap = self.android_provider.check_capability()
        active_loc = self.config.active_location

        reported_coords = None
        if target_device and self.android_provider.adb.is_available():
            try:
                reported_coords = self.android_provider.adb.get_reported_location(target_device.serial)
            except Exception:
                pass

        spoofing_active = active_loc is not None and cap.available

        return {
            "device": target_device,
            "capability": cap,
            "target_location": active_loc,
            "reported_coordinates": reported_coords,
            "spoofing_active": spoofing_active,
            "mock_provider_status": "ACTIVE" if spoofing_active else "INACTIVE",
        }

    # Backward compatibility / legacy support
    def set_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
        altitude: Optional[float] = None,
        accuracy: Optional[float] = None,
        target_provider: Optional[str] = None,
    ) -> Tuple[Location, Dict[str, OperationResult]]:
        resolved_name = location_name

        if location_name and (latitude is None or longitude is None):
            geo_loc = self.geocoder.geocode(location_name)
            lat = geo_loc.latitude
            lon = geo_loc.longitude
            resolved_name = geo_loc.name
        elif latitude is not None and longitude is not None:
            coords = Coordinates(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                accuracy=accuracy,
            )
            lat = coords.latitude
            lon = coords.longitude
            if not resolved_name:
                resolved_name = self.geocoder.reverse_geocode(lat, lon)
        else:
            raise ValidationError(
                message="Provide coordinates (e.g. 'locspoof 55.554250 55.765611') or use --lat and --lon.",
                suggestion="Example: locspoof '55°33\\'15.3\"N 55°45\\'56.2\"E'",
            )

        loc = Location(
            latitude=lat,
            longitude=lon,
            altitude=altitude,
            accuracy=accuracy,
            name=resolved_name,
            source=LocationSource.CONFIG,
        )

        self.config.active_location = loc
        save_config(self.config)

        if target_provider:
            p = self.provider_manager.get_provider(target_provider)
            if not p:
                raise LocSpoofError(f"Provider '{target_provider}' not found.")
            results = {p.name: p.apply_location(loc)}
        else:
            results = self.provider_manager.apply_to_all(loc)

        return loc, results

    def get_status(self) -> Dict:
        configured_loc = self.config.active_location
        capabilities = self.provider_manager.get_all_capabilities()
        signals = self.provider_manager.collect_all_signals()
        verification = self.verification_engine.verify(
            signals=signals,
            anchor_coords=configured_loc.coordinates if configured_loc else None,
        )
        return {
            "configured_location": configured_loc,
            "capabilities": capabilities,
            "signals": signals,
            "verification": verification,
        }

    def verify(self) -> LocationVerification:
        signals = self.provider_manager.collect_all_signals()
        anchor = self.config.active_location.coordinates if self.config.active_location else None
        return self.verification_engine.verify(signals=signals, anchor_coords=anchor)

    def reset(self, target_provider: Optional[str] = None) -> Dict[str, OperationResult]:
        if target_provider:
            p = self.provider_manager.get_provider(target_provider)
            if not p:
                raise LocSpoofError(f"Provider '{target_provider}' not found.")
            results = {p.name: p.reset()}
        else:
            results = self.provider_manager.reset_all()
            self.config.active_location = None
            save_config(self.config)
        return results
