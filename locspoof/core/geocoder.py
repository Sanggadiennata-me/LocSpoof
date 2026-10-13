"""
Geocoding and Reverse Geocoding service for locspoof.
Uses OpenStreetMap Nominatim with strict rate limiting, custom User-Agent, and local caching.
Completely decoupled from the core location engine.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import httpx
from platformdirs import user_cache_dir

from locspoof.core.exceptions import LocSpoofError
from locspoof.core.models import Coordinates, Location, LocationSource
from locspoof.utils.logger import logger


class Geocoder:
    """
    Independent geocoding service providing forward and reverse geocoding.
    """
    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "locspoof-security-tool/0.1.0 (https://github.com/r3x/locspoof)"

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(user_cache_dir("locspoof"))
        self.cache_file = self.cache_dir / "geocoding_cache.json"
        self._cache: Dict[str, Dict] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict]:
        if not self.cache_enabled or not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self) -> None:
        if not self.cache_enabled:
            return
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as exc:
            logger.debug(f"Failed to write geocoding cache: {exc}")

    def geocode(self, query: str, timeout: float = 6.0) -> Location:
        """
        Convert a location name (e.g. 'Jakarta', 'Tokyo') to Coordinates and Location.
        """
        norm_query = query.strip().lower()
        if not norm_query:
            raise LocSpoofError("Location query cannot be empty.")

        cache_key = f"geo:{norm_query}"
        if cache_key in self._cache:
            data = self._cache[cache_key]
            logger.debug(f"Geocoding cache hit for '{query}'")
            return Location(
                latitude=data["lat"],
                longitude=data["lon"],
                name=data["display_name"],
                source=LocationSource.GEOCODER,
                extra=data,
            )

        try:
            headers = {"User-Agent": self.USER_AGENT}
            params = {"q": query, "format": "json", "limit": 1}
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(f"{self.NOMINATIM_URL}/search", params=params, headers=headers)
                resp.raise_for_status()
                results = resp.json()

            if not results:
                raise LocSpoofError(
                    message=f"Location '{query}' could not be resolved.",
                    detail="Nominatim returned no matching coordinates for this query.",
                    suggestion="Try using more specific search terms (e.g., 'Jakarta, Indonesia') or provide exact --lat and --lon.",
                )

            item = results[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            display_name = item.get("display_name", query)

            # Store in cache
            self._cache[cache_key] = {
                "lat": lat,
                "lon": lon,
                "display_name": display_name,
                "type": item.get("type"),
                "importance": item.get("importance"),
            }
            self._save_cache()

            return Location(
                latitude=lat,
                longitude=lon,
                name=display_name,
                source=LocationSource.GEOCODER,
                extra=item,
            )
        except httpx.HTTPError as exc:
            raise LocSpoofError(
                message=f"Network error during geocoding for '{query}'.",
                detail=str(exc),
                suggestion="Check your internet connectivity or supply exact coordinates with --lat and --lon.",
            ) from exc

    def reverse_geocode(self, lat: float, lon: float, timeout: float = 6.0) -> Optional[str]:
        """
        Lookup city / country name from lat and lon.
        """
        cache_key = f"rev:{round(lat, 4)}:{round(lon, 4)}"
        if cache_key in self._cache:
            return self._cache[cache_key].get("display_name")

        try:
            headers = {"User-Agent": self.USER_AGENT}
            params = {"lat": lat, "lon": lon, "format": "json"}
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(f"{self.NOMINATIM_URL}/reverse", params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    name = data.get("display_name")
                    if name:
                        self._cache[cache_key] = {"display_name": name, "address": data.get("address", {})}
                        self._save_cache()
                        return name
        except Exception as exc:
            logger.debug(f"Reverse geocoding failed: {exc}")
        return None
