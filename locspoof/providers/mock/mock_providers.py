"""
Mock providers for offline testing, unit tests, and CI/CD pipelines.
"""

from typing import Optional
from locspoof.core.models import (
    Coordinates,
    Location,
    LocationSignal,
    LocationSource,
    OperationResult,
    ProviderCapability,
)
from locspoof.providers.base import BaseProvider


class MockGPSProvider(BaseProvider):
    """Simulates a hardware/device GPS provider."""

    def __init__(
        self,
        name: str = "mock_gps",
        is_available: bool = True,
        initial_coords: Optional[Coordinates] = None,
        city: str = "Jakarta",
        country: str = "Indonesia",
    ):
        self._name = name
        self.is_available = is_available
        self.current_coords = initial_coords or Coordinates(latitude=-6.2088, longitude=106.8456)
        self.city = city
        self.country = country

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Mock GPS hardware provider for testing"

    def check_capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            available=self.is_available,
            status_summary="READY" if self.is_available else "UNAVAILABLE",
        )

    def apply_location(self, location: Location) -> OperationResult:
        self.current_coords = location.coordinates
        if location.name:
            self.city = location.name
        return OperationResult(success=True, message=f"Mock GPS set to {location.latitude}, {location.longitude}")

    def get_current_signal(self) -> LocationSignal:
        return LocationSignal(
            source=LocationSource.GPS,
            source_name=self.name,
            coordinates=self.current_coords,
            city=self.city,
            country=self.country,
        )

    def reset(self) -> OperationResult:
        self.current_coords = None
        return OperationResult(success=True, message="Mock GPS reset")


class MockBrowserProvider(BaseProvider):
    """Simulates a browser geolocation provider."""

    def __init__(
        self,
        name: str = "mock_browser",
        is_available: bool = True,
        initial_coords: Optional[Coordinates] = None,
        city: str = "Jakarta",
    ):
        self._name = name
        self.is_available = is_available
        self.current_coords = initial_coords or Coordinates(latitude=-6.2088, longitude=106.8456)
        self.city = city

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Mock Browser Geolocation CDP provider"

    def check_capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            available=self.is_available,
            status_summary="READY" if self.is_available else "UNAVAILABLE",
        )

    def apply_location(self, location: Location) -> OperationResult:
        self.current_coords = location.coordinates
        return OperationResult(success=True, message=f"Mock Browser location overridden to {location.latitude}, {location.longitude}")

    def get_current_signal(self) -> LocationSignal:
        return LocationSignal(
            source=LocationSource.BROWSER,
            source_name=self.name,
            coordinates=self.current_coords,
            city=self.city,
        )

    def reset(self) -> OperationResult:
        self.current_coords = None
        return OperationResult(success=True, message="Mock Browser geolocation cleared")


class MockNetworkProvider(BaseProvider):
    """Simulates an IP/network egress location provider."""

    def __init__(
        self,
        name: str = "mock_network",
        is_available: bool = True,
        coords: Optional[Coordinates] = None,
        ip: str = "198.51.100.42",
        city: str = "Montreal",
        country: str = "Canada",
        timezone_name: str = "America/Toronto",
    ):
        self._name = name
        self.is_available = is_available
        self.coords = coords or Coordinates(latitude=45.5017, longitude=-73.5673)
        self.ip = ip
        self.city = city
        self.country = country
        self.timezone_name = timezone_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Mock Network Egress IP Geo provider"

    def check_capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            available=self.is_available,
            status_summary="READY",
        )

    def apply_location(self, location: Location) -> OperationResult:
        return OperationResult(
            success=False,
            message="Cannot directly change public egress IP via coordinate assignment. Use proxy/tunnel.",
        )

    def get_current_signal(self) -> LocationSignal:
        return LocationSignal(
            source=LocationSource.NETWORK_IP,
            source_name=self.name,
            coordinates=self.coords,
            ip_address=self.ip,
            city=self.city,
            country=self.country,
            timezone_name=self.timezone_name,
        )

    def reset(self) -> OperationResult:
        return OperationResult(success=True, message="Mock Network reset")
