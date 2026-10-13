"""
Domain models and validation schemas for locspoof.
Uses Pydantic v2 for robust validation of WGS84 coordinates and multi-signal location entities.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LocationSource(str, Enum):
    """Source categories of location signals."""
    CONFIG = "config"
    GPS = "gps"
    ANDROID = "android"
    EMULATOR = "emulator"
    BROWSER = "browser"
    NETWORK_IP = "network_ip"
    GEOCODER = "geocoder"
    MOCK = "mock"


class ConsistencyLevel(str, Enum):
    """Verification outcome levels."""
    MATCH = "MATCH"
    WARNING = "WARNING"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class Coordinates(BaseModel):
    """
    WGS84 Geodetic Coordinates representation with strict boundary validation.
    """
    latitude: float = Field(..., description="Latitude in decimal degrees (-90 to +90)")
    longitude: float = Field(..., description="Longitude in decimal degrees (-180 to +180)")
    altitude: Optional[float] = Field(default=None, description="Altitude in meters above WGS84 ellipsoid")
    accuracy: Optional[float] = Field(default=None, description="Horizontal accuracy radius in meters")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < -90.0 or v > 90.0:
            raise ValueError(f"Latitude must be between -90.0 and 90.0 degrees (got {v})")
        return round(v, 7)

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < -180.0 or v > 180.0:
            raise ValueError(f"Longitude must be between -180.0 and 180.0 degrees (got {v})")
        return round(v, 7)

    @field_validator("accuracy")
    @classmethod
    def validate_accuracy(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0.0:
            raise ValueError(f"Accuracy must be non-negative (got {v})")
        return v


class Location(BaseModel):
    """
    Comprehensive Location record.
    """
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: LocationSource = LocationSource.CONFIG
    name: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    @property
    def coordinates(self) -> Coordinates:
        return Coordinates(
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            accuracy=self.accuracy,
        )


class LocationSignal(BaseModel):
    """
    An observed or extracted location signal from a specific source (e.g. Browser, Android, IP).
    """
    source: LocationSource
    source_name: str
    coordinates: Optional[Coordinates] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    timezone_name: Optional[str] = None
    ip_address: Optional[str] = None
    raw_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    error_message: Optional[str] = None


class LocationMismatch(BaseModel):
    """
    A detected inconsistency between two or more location signals.
    """
    signal_a: str
    signal_b: str
    distance_km: Optional[float] = None
    description: str
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL


class LocationVerification(BaseModel):
    """
    Consolidated verification outcome across all checked location signals.
    """
    consistency: ConsistencyLevel
    consistency_score: int = Field(..., ge=0, le=100)
    signals: List[LocationSignal] = Field(default_factory=list)
    mismatches: List[LocationMismatch] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProviderCapability(BaseModel):
    """
    Capability description of a provider on the current host.
    """
    name: str
    available: bool
    status_summary: str
    details: Dict[str, Any] = Field(default_factory=dict)
    suggestion: Optional[str] = None


class OperationResult(BaseModel):
    """
    Result of executing a provider operation (set, reset, launch, etc.).
    """
    success: bool
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
