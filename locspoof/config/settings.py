"""
Configuration settings schema for locspoof using Pydantic.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from locspoof.core.models import Location


class BrowserConfig(BaseModel):
    browser_type: str = Field(default="chromium", description="Browser engine: chromium, chrome, edge, firefox")
    headless: bool = Field(default=False, description="Whether to launch browser in headless mode")
    profile_dir: Optional[str] = Field(default=None, description="Custom browser user data directory")
    remote_debugging_port: Optional[int] = Field(default=9222, description="Remote debugging port for CDP")


class AndroidConfig(BaseModel):
    preferred_device: Optional[str] = Field(default=None, description="Specific serial ID of device or emulator")
    mock_app_package: Optional[str] = Field(default=None, description="Package name of test/mock provider app if any")
    timeout: float = Field(default=10.0, description="ADB command timeout in seconds")


class NetworkConfig(BaseModel):
    proxy_url: Optional[str] = Field(default=None, description="SOCKS5 or HTTP proxy URL (e.g. socks5://127.0.0.1:9050)")
    geoip_api_url: str = Field(default="https://ipapi.co/json/", description="Public GeoIP lookup endpoint")
    timeout: float = Field(default=8.0, description="Network timeout in seconds")


class VerificationConfig(BaseModel):
    distance_threshold_km: float = Field(default=50.0, description="Maximum tolerance before flagging distance mismatch")
    check_timezone: bool = Field(default=True, description="Whether to verify timezone against target location")
    check_ip_egress: bool = Field(default=True, description="Whether to inspect public egress IP in verification")


class Config(BaseModel):
    """Root configuration model."""
    active_location: Optional[Location] = None
    enabled_providers: List[str] = Field(default_factory=lambda: ["android", "browser", "network"])
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    android: AndroidConfig = Field(default_factory=AndroidConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
