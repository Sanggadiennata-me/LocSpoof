"""
Public Egress IP and GeoIP resolver.
Queries standard public GeoIP endpoints with optional proxy configuration.
"""

from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel

from locspoof.core.exceptions import LocSpoofError
from locspoof.core.models import Coordinates
from locspoof.utils.logger import logger


class GeoIPData(BaseModel):
    ip: str
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    org: Optional[str] = None
    raw: Dict[str, Any] = {}

    @property
    def coordinates(self) -> Optional[Coordinates]:
        if self.latitude is not None and self.longitude is not None:
            return Coordinates(latitude=self.latitude, longitude=self.longitude)
        return None


class IPResolver:
    """
    Service to resolve the current external IP and GeoIP metadata.
    """

    DEFAULT_ENDPOINTS = [
        "https://ipapi.co/json/",
        "https://ipwho.is/",
    ]

    def __init__(self, proxy_url: Optional[str] = None, timeout: float = 6.0):
        self.proxy_url = proxy_url
        self.timeout = timeout

    def resolve(self) -> GeoIPData:
        """
        Query public GeoIP endpoint to obtain egress IP and approximate physical location.
        """
        client_kwargs: Dict[str, Any] = {"timeout": self.timeout}
        if self.proxy_url:
            client_kwargs["proxy"] = self.proxy_url

        last_error = None
        for endpoint in self.DEFAULT_ENDPOINTS:
            try:
                with httpx.Client(**client_kwargs) as client:
                    resp = client.get(endpoint)
                    if resp.status_code == 200:
                        data = resp.json()
                        return self._parse_response(endpoint, data)
            except Exception as exc:
                last_error = exc
                logger.debug(f"GeoIP endpoint {endpoint} failed: {exc}")

        raise LocSpoofError(
            message="Failed to resolve public egress IP and GeoIP data.",
            detail=str(last_error) if last_error else "All GeoIP endpoints failed.",
            suggestion="Check your internet connection or verify proxy settings.",
        )

    def _parse_response(self, endpoint: str, data: Dict[str, Any]) -> GeoIPData:
        if "ipapi.co" in endpoint:
            lat = data.get("latitude")
            lon = data.get("longitude")
            return GeoIPData(
                ip=data.get("ip", "Unknown"),
                city=data.get("city"),
                region=data.get("region"),
                country=data.get("country_name"),
                latitude=float(lat) if lat is not None else None,
                longitude=float(lon) if lon is not None else None,
                timezone=data.get("timezone"),
                org=data.get("org"),
                raw=data,
            )
        elif "ipwho.is" in endpoint:
            lat = data.get("latitude")
            lon = data.get("longitude")
            return GeoIPData(
                ip=data.get("ip", "Unknown"),
                city=data.get("city"),
                region=data.get("region"),
                country=data.get("country"),
                latitude=float(lat) if lat is not None else None,
                longitude=float(lon) if lon is not None else None,
                timezone=data.get("timezone", {}).get("id") if isinstance(data.get("timezone"), dict) else None,
                org=data.get("connection", {}).get("org") if isinstance(data.get("connection"), dict) else None,
                raw=data,
            )
        return GeoIPData(ip=data.get("ip", "Unknown"), raw=data)
