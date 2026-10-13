"""
Network & IP Geolocation Provider for locspoof.
Monitors egress IP geolocation and manages proxy testing abstractions.
"""

from typing import Optional

from locspoof.core.exceptions import LocSpoofError
from locspoof.core.models import (
    Coordinates,
    Location,
    LocationSignal,
    LocationSource,
    OperationResult,
    ProviderCapability,
)
from locspoof.providers.base import BaseProvider
from locspoof.providers.network.ip_resolver import GeoIPData, IPResolver
from locspoof.utils.logger import logger


class NetworkProvider(BaseProvider):
    """
    Provider representing Network Layer & Public IP Geolocation.
    """

    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.resolver = IPResolver(proxy_url=proxy_url)
        self._cached_geoip: Optional[GeoIPData] = None

    @property
    def name(self) -> str:
        return "network"

    @property
    def description(self) -> str:
        return "Network & IP Egress Geolocation Provider"

    def set_proxy(self, proxy_url: Optional[str]) -> None:
        self.proxy_url = proxy_url
        self.resolver = IPResolver(proxy_url=proxy_url)
        self._cached_geoip = None

    def check_capability(self) -> ProviderCapability:
        summary = "CONFIGURED (Direct Egress)"
        if self.proxy_url:
            summary = f"CONFIGURED (Proxy: {self.proxy_url})"

        return ProviderCapability(
            name=self.name,
            available=True,
            status_summary=summary,
            details={"proxy_url": self.proxy_url},
        )

    def apply_location(self, location: Location) -> OperationResult:
        # Crucial technical honesty requirement:
        # Setting coordinates NEVER changes public IP automatically.
        return OperationResult(
            success=False,
            message=(
                "Changing GPS coordinates does NOT alter your public IP geolocation. "
                "IP geolocation is determined by your network route/ISP. "
                "To align IP with target coordinates, configure a proxy: 'locspoof network proxy --url <PROXY_URL>'."
            ),
            details={"target_lat": location.latitude, "target_lon": location.longitude},
        )

    def test_connection(self) -> GeoIPData:
        """Query egress IP and update cache."""
        data = self.resolver.resolve()
        self._cached_geoip = data
        return data

    def get_current_signal(self) -> LocationSignal:
        try:
            data = self._cached_geoip or self.resolver.resolve()
            self._cached_geoip = data
            return LocationSignal(
                source=LocationSource.NETWORK_IP,
                source_name="Public IP Egress",
                coordinates=data.coordinates,
                city=data.city,
                region=data.region,
                country=data.country,
                timezone_name=data.timezone,
                ip_address=data.ip,
                raw_details={"isp": data.org, "proxy": self.proxy_url},
                is_active=True,
            )
        except Exception as exc:
            logger.debug(f"Network signal probe failed: {exc}")
            return LocationSignal(
                source=LocationSource.NETWORK_IP,
                source_name="Public IP Egress",
                coordinates=None,
                is_active=False,
                error_message=str(exc),
            )

    def reset(self) -> OperationResult:
        self.set_proxy(None)
        return OperationResult(success=True, message="Network proxy configuration cleared (direct connection restored).")
