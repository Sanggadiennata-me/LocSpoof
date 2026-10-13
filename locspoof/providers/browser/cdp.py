"""
Chrome DevTools Protocol (CDP) Geolocation Interceptor.
Communicates with Chromium-based browsers via remote debugging port to override geolocation.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
import httpx
import websockets

from locspoof.core.exceptions import LocSpoofError
from locspoof.utils.logger import logger


class CDPClient:
    """
    Client for interacting with Chrome DevTools Protocol endpoints.
    Sends Emulation.setGeolocationOverride directly to active browser targets.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 9222):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    def is_reachable(self) -> bool:
        """Check if remote debugging port is open and responding."""
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{self.base_url}/json/version")
                return res.status_code == 200
        except Exception:
            return False

    def get_targets(self) -> List[Dict[str, Any]]:
        """List active browser tabs / inspectable targets."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/json/list")
                if res.status_code == 200:
                    return res.json()
        except Exception as exc:
            logger.debug(f"Failed to fetch CDP targets: {exc}")
        return []

    def get_browser_version(self) -> Optional[Dict[str, Any]]:
        """Get browser metadata via CDP."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/json/version")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            return None

    def override_geolocation(
        self,
        latitude: float,
        longitude: float,
        accuracy: float = 10.0,
        timeout: float = 4.0,
    ) -> bool:
        """
        Connect to browser CDP websocket and apply Emulation.setGeolocationOverride.
        """
        try:
            return asyncio.run(self._async_override_geolocation(latitude, longitude, accuracy, timeout))
        except Exception as exc:
            logger.debug(f"CDP geolocation override error: {exc}")
            return False

    async def _async_override_geolocation(
        self,
        latitude: float,
        longitude: float,
        accuracy: float,
        timeout: float,
    ) -> bool:
        # 1. Fetch targets
        targets = self.get_targets()
        page_targets = [t for t in targets if t.get("type") == "page" and "webSocketDebuggerUrl" in t]

        if not page_targets:
            # Fallback to browser websocket
            ver = self.get_browser_version()
            browser_ws = ver.get("webSocketDebuggerUrl") if ver else None
            ws_urls = [browser_ws] if browser_ws else []
        else:
            ws_urls = [t["webSocketDebuggerUrl"] for t in page_targets]

        success_any = False
        for ws_url in ws_urls:
            try:
                async with websockets.connect(ws_url, close_timeout=timeout) as ws:
                    # 1. Grant geolocation permissions
                    cmd_grant = {
                        "id": 1,
                        "method": "Browser.grantPermissions",
                        "params": {"permissions": ["geolocation"]},
                    }
                    await ws.send(json.dumps(cmd_grant))

                    # 2. Set Geolocation Override
                    cmd_override = {
                        "id": 2,
                        "method": "Emulation.setGeolocationOverride",
                        "params": {
                            "latitude": latitude,
                            "longitude": longitude,
                            "accuracy": accuracy,
                        },
                    }
                    await ws.send(json.dumps(cmd_override))
                    success_any = True
                    logger.debug(f"CDP Geolocation overridden on {ws_url}: {latitude}, {longitude}")
            except Exception as exc:
                logger.debug(f"Failed to send CDP command to {ws_url}: {exc}")

        return success_any
