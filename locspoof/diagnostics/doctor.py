"""
Doctor Diagnostics Engine for locspoof.
Performs system, dependency, and permission health audits.
"""

import os
import sys
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

from locspoof.config.storage import get_config_dir, get_config_path
from locspoof.providers.android.adb_client import AdbClient
from locspoof.providers.browser.provider import BrowserProvider
from locspoof.utils.process import find_executable, safe_run


class DiagnosticItem(BaseModel):
    name: str
    status: str  # "OK", "WARN", "ERROR"
    message: str
    suggestion: Optional[str] = None


class DoctorReport(BaseModel):
    items: List[DiagnosticItem]
    passed_count: int
    warn_count: int
    error_count: int

    @property
    def is_healthy(self) -> bool:
        return self.error_count == 0


class Doctor:
    """
    Executes diagnostics on runtime environment and dependencies.
    """

    def run_diagnostics(self) -> DoctorReport:
        items: List[DiagnosticItem] = []

        # 1. Python Runtime check
        py_ver = sys.version_info
        py_str = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
        if py_ver >= (3, 10):
            items.append(
                DiagnosticItem(
                    name="Python Runtime",
                    status="OK",
                    message=f"Python v{py_str} (Supported: >= 3.10)",
                )
            )
        else:
            items.append(
                DiagnosticItem(
                    name="Python Runtime",
                    status="ERROR",
                    message=f"Python v{py_str} is outdated.",
                    suggestion="Upgrade Python to version 3.10 or higher.",
                )
            )

        # 2. Configuration & Directory permissions
        cfg_dir = get_config_dir()
        cfg_path = get_config_path()
        try:
            cfg_dir.mkdir(parents=True, exist_ok=True)
            test_file = cfg_dir / ".doctor_write_test"
            test_file.write_text("ok")
            test_file.unlink()
            items.append(
                DiagnosticItem(
                    name="Configuration Storage",
                    status="OK",
                    message=f"Config path '{cfg_path}' is accessible and writable.",
                )
            )
        except Exception as exc:
            items.append(
                DiagnosticItem(
                    name="Configuration Storage",
                    status="ERROR",
                    message=f"Cannot write to config directory '{cfg_dir}': {exc}",
                    suggestion="Check file permissions on your user home/config directory.",
                )
            )

        # 3. Network Egress & GeoIP endpoint
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.get("https://1.1.1.1", follow_redirects=True)
                if res.status_code < 500:
                    items.append(
                        DiagnosticItem(
                            name="Network Connectivity",
                            status="OK",
                            message="Outbound HTTPS network egress verified.",
                        )
                    )
                else:
                    items.append(
                        DiagnosticItem(
                            name="Network Connectivity",
                            status="WARN",
                            message=f"Egress check returned status {res.status_code}",
                            suggestion="Check network firewall or proxy settings.",
                        )
                    )
        except Exception as exc:
            items.append(
                DiagnosticItem(
                    name="Network Connectivity",
                    status="WARN",
                    message=f"Outbound network test failed: {exc}",
                    suggestion="Verify internet connection if you plan to use online Geocoding or GeoIP verification.",
                )
            )

        # 4. ADB Binary & Devices
        adb_client = AdbClient()
        if adb_client.is_available():
            try:
                ver_res = safe_run([adb_client.adb_path, "version"], timeout=4.0)
                devices = adb_client.list_devices()
                emulators = [d for d in devices if d.is_emulator]
                if emulators:
                    items.append(
                        DiagnosticItem(
                            name="Android / ADB",
                            status="OK",
                            message=f"ADB active ({len(devices)} device(s), active emulator: {emulators[0].serial})",
                        )
                    )
                elif devices:
                    items.append(
                        DiagnosticItem(
                            name="Android / ADB",
                            status="OK",
                            message=f"ADB active ({len(devices)} physical device(s) connected)",
                        )
                    )
                else:
                    items.append(
                        DiagnosticItem(
                            name="Android / ADB",
                            status="WARN",
                            message=f"ADB binary found at '{adb_client.adb_path}', but no devices or emulators connected.",
                            suggestion="Start an Android Emulator or connect a device with USB Debugging enabled.",
                        )
                    )
            except Exception as exc:
                items.append(
                    DiagnosticItem(
                        name="Android / ADB",
                        status="WARN",
                        message=f"ADB present but query failed: {exc}",
                        suggestion="Run 'adb kill-server && adb start-server'.",
                    )
                )
        else:
            items.append(
                DiagnosticItem(
                    name="Android / ADB",
                    status="WARN",
                    message="Android Debug Bridge (adb) not found in system PATH.",
                    suggestion="Install Android SDK Platform-Tools ('sudo apt install adb' or via Android Studio) if testing Android apps.",
                )
            )

        # 5. Browser Automation Engine
        browser_provider = BrowserProvider()
        browser_cap = browser_provider.check_capability()
        if browser_cap.available:
            browser_path = browser_cap.details.get("browser_binary", "Browser")
            items.append(
                DiagnosticItem(
                    name="Browser Engine",
                    status="OK",
                    message=f"Found {os.path.basename(browser_path)} ('{browser_path}')",
                )
            )
        else:
            items.append(
                DiagnosticItem(
                    name="Browser Engine",
                    status="WARN",
                    message="No Chromium/Chrome/Brave browser executable found.",
                    suggestion="Install Google Chrome or Chromium to enable browser geolocation testing.",
                )
            )

        passed = sum(1 for i in items if i.status == "OK")
        warns = sum(1 for i in items if i.status == "WARN")
        errors = sum(1 for i in items if i.status == "ERROR")

        return DoctorReport(
            items=items,
            passed_count=passed,
            warn_count=warns,
            error_count=errors,
        )
