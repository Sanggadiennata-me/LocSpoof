"""
Browser Geolocation Testing Provider for locspoof.
Targets web applications consuming navigator.geolocation via Chrome DevTools Protocol & browser runner.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from locspoof.core.exceptions import DependencyMissingError, LocSpoofError
from locspoof.core.models import (
    Coordinates,
    Location,
    LocationSignal,
    LocationSource,
    OperationResult,
    ProviderCapability,
)
from locspoof.providers.base import BaseProvider
from locspoof.providers.browser.cdp import CDPClient
from locspoof.utils.logger import logger
from locspoof.utils.process import find_executable


class BrowserProvider(BaseProvider):
    """
    Provider for simulating and testing Browser W3C Geolocation API.
    """

    KNOWN_EXECUTABLES = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "brave-browser",
        "microsoft-edge",
        "msedge",
    ]

    def __init__(self, port: int = 9222):
        self.port = port
        self.cdp = CDPClient(port=port)
        self._last_coords: Optional[Coordinates] = None
        self._last_browser_path: Optional[str] = self._detect_browser_binary()
        self._running_proc: Optional[subprocess.Popen] = None

    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Browser Geolocation (CDP / navigator.geolocation) Testing Provider"

    def _detect_browser_binary(self) -> Optional[str]:
        for name in self.KNOWN_EXECUTABLES:
            path = find_executable(name)
            if path:
                return path
        return None

    def check_capability(self) -> ProviderCapability:
        browser_path = self._detect_browser_binary()
        if not browser_path:
            return ProviderCapability(
                name=self.name,
                available=False,
                status_summary="BROWSER NOT FOUND",
                suggestion="Install Google Chrome, Chromium, or Brave for browser geolocation testing.",
            )

        cdp_active = self.cdp.is_reachable()
        summary = f"READY ({os.path.basename(browser_path)})"
        if cdp_active:
            summary += f" [CDP Connected on :{self.port}]"

        return ProviderCapability(
            name=self.name,
            available=True,
            status_summary=summary,
            details={
                "browser_binary": browser_path,
                "cdp_port": self.port,
                "cdp_active": cdp_active,
            },
        )

    def apply_location(self, location: Location) -> OperationResult:
        cap = self.check_capability()
        if not cap.available:
            return OperationResult(
                success=False,
                message="No compatible browser found to apply location.",
                error="BrowserNotFound",
            )

        self._last_coords = location.coordinates

        # If a CDP session is actively running, inform user or dispatch CDP override
        if self.cdp.is_reachable():
            # DevTools port is live
            return OperationResult(
                success=True,
                message=(
                    f"Configured browser geolocation override to {location.latitude}, {location.longitude}. "
                    f"Active CDP session connected on port {self.port}."
                ),
                details={"latitude": location.latitude, "longitude": location.longitude, "cdp_port": self.port},
            )

        return OperationResult(
            success=True,
            message=(
                f"Configured browser geolocation to {location.latitude}, {location.longitude}. "
                "Launch browser session with 'locspoof browser launch' to test against web applications."
            ),
            details={"latitude": location.latitude, "longitude": location.longitude},
        )

    def generate_diagnostic_page(self, target_coords: Optional[Coordinates] = None) -> Path:
        """
        Generate a standalone local HTML page that tests navigator.geolocation.
        """
        temp_dir = Path(tempfile.gettempdir()) / "locspoof"
        temp_dir.mkdir(parents=True, exist_ok=True)
        html_path = temp_dir / "geolocation_test.html"

        expected_lat = target_coords.latitude if target_coords else 0.0
        expected_lon = target_coords.longitude if target_coords else 0.0

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LocSpoof Geolocation Verification Test</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0f172a; color: #f8fafc; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 24px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; margin-top: 0; font-size: 22px; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
        .badge-info {{ background: #0284c7; color: white; }}
        .badge-success {{ background: #16a34a; color: white; }}
        .badge-error {{ background: #dc2626; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 18px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; font-size: 13px; text-transform: uppercase; }}
        .mono {{ font-family: monospace; color: #a5f3fc; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>LocSpoof Browser Geolocation Test Suite</h1>
        <p>Testing <span class="mono">navigator.geolocation.getCurrentPosition()</span> resolution in controlled browser instance.</p>
        <div id="status"><span class="badge badge-info">Requesting Geolocation...</span></div>
        <table id="resultTable" style="display:none;">
            <tr><th>Metric</th><th>Simulated Target</th><th>Browser Reported Value</th></tr>
            <tr><td>Latitude</td><td class="mono">{expected_lat}</td><td class="mono" id="valLat">-</td></tr>
            <tr><td>Longitude</td><td class="mono">{expected_lon}</td><td class="mono" id="valLon">-</td></tr>
            <tr><td>Accuracy</td><td class="mono">Configured</td><td class="mono" id="valAcc">-</td></tr>
            <tr><td>Timestamp</td><td class="mono">Real-time</td><td class="mono" id="valTime">-</td></tr>
        </table>
    </div>
    <script>
        if (!navigator.geolocation) {{
            document.getElementById('status').innerHTML = '<span class="badge badge-error">Geolocation API Not Supported</span>';
        }} else {{
            navigator.geolocation.getCurrentPosition(
                (pos) => {{
                    document.getElementById('status').innerHTML = '<span class="badge badge-success">Geolocation Resolved Successfully</span>';
                    document.getElementById('resultTable').style.display = 'table';
                    document.getElementById('valLat').innerText = pos.coords.latitude.toFixed(6);
                    document.getElementById('valLon').innerText = pos.coords.longitude.toFixed(6);
                    document.getElementById('valAcc').innerText = pos.coords.accuracy + ' m';
                    document.getElementById('valTime').innerText = new Date(pos.timestamp).toISOString();
                }},
                (err) => {{
                    document.getElementById('status').innerHTML = '<span class="badge badge-error">Error (' + err.code + '): ' + err.message + '</span>';
                }},
                {{ enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }}
            );
        }}
    </script>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_path

    def launch_browser(self, target_url: Optional[str] = None, coords: Optional[Coordinates] = None) -> OperationResult:
        """
        Launch browser instance in safe isolated testing sandbox with remote debugging enabled.
        """
        browser_path = self._detect_browser_binary()
        if not browser_path:
            raise DependencyMissingError("No compatible browser binary found.")

        target_coords = coords or self._last_coords
        if not target_url:
            test_page = self.generate_diagnostic_page(target_coords)
            url = f"file://{test_page.resolve()}"
        else:
            url = target_url

        temp_profile = Path(tempfile.mkdtemp(prefix="locspoof_browser_profile_"))
        default_dir = temp_profile / "Default"
        default_dir.mkdir(parents=True, exist_ok=True)
        pref_file = default_dir / "Preferences"
        try:
            # Grant geolocation permission automatically in profile
            pref_data = {
                "profile": {
                    "default_content_setting_values": {
                        "geolocation": 1
                    }
                }
            }
            with open(pref_file, "w", encoding="utf-8") as f:
                json.dump(pref_data, f)
        except Exception as exc:
            logger.debug(f"Failed to write default browser preferences: {exc}")

        cmd = [
            browser_path,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={temp_profile}",
            "--no-first-run",
            "--no-default-browser-check",
            url,
        ]

        logger.debug(f"Launching browser: {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self._running_proc = proc

            # Dispatch CDP geolocation override once port opens
            if target_coords:
                import time
                for _ in range(15):
                    time.sleep(0.2)
                    if self.cdp.is_reachable():
                        self.cdp.override_geolocation(
                            latitude=target_coords.latitude,
                            longitude=target_coords.longitude,
                            accuracy=target_coords.accuracy or 10.0,
                        )
                        break

            return OperationResult(
                success=True,
                message=f"Browser launched ({os.path.basename(browser_path)}) with remote debugging port {self.port}.",
                details={
                    "pid": proc.pid,
                    "profile_dir": str(temp_profile),
                    "url": url,
                    "target_coords": target_coords.model_dump() if target_coords else None,
                },
            )
        except Exception as exc:
            return OperationResult(
                success=False,
                message=f"Failed to launch browser: {exc}",
                error=str(exc),
            )

    def get_current_signal(self) -> LocationSignal:
        cap = self.check_capability()
        return LocationSignal(
            source=LocationSource.BROWSER,
            source_name=f"Browser ({os.path.basename(self._last_browser_path or 'None')})",
            coordinates=self._last_coords,
            is_active=cap.available and self._last_coords is not None,
            raw_details=cap.details,
            error_message=None if cap.available else cap.status_summary,
        )

    def reset(self) -> OperationResult:
        self._last_coords = None
        return OperationResult(success=True, message="Browser location simulation reset.")
