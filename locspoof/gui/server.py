"""
LocSpoof Web GUI Server and Desktop Launcher.
Serves the React Flat Design Web Application and provides local device bridge APIs.
"""

import http.server
import json
import os
import socketserver
import sys
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "web" / "dist"

class LocSpoofWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        # API: List connected Android devices
        if parsed.path == "/api/devices":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            try:
                from locspoof.core.service import LocationService
                svc = LocationService()
                devices = [d.model_dump() for d in svc.list_devices()]
                self.wfile.write(json.dumps({"success": True, "devices": devices}).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"success": False, "error": str(e), "devices": []}).encode())
            return

        # API: Status
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            try:
                from locspoof.core.service import LocationService
                svc = LocationService()
                status = svc.get_spoof_status()
                dev = status["device"].model_dump() if status["device"] else None
                cap = status["capability"].model_dump() if status["capability"] else None
                reported = status["reported_coordinates"].model_dump() if status["reported_coordinates"] else None
                self.wfile.write(json.dumps({
                    "success": True,
                    "device": dev,
                    "capability": cap,
                    "reported": reported,
                    "spoofing_active": status["spoofing_active"]
                }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"success": False, "error": str(e), "spoofing_active": False}).encode())
            return

        # Fallback to SPA index.html for router paths
        file_path = DIST_DIR / parsed.path.lstrip("/")
        if not file_path.exists() and not parsed.path.startswith("/api/"):
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if parsed.path == "/api/spoof":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            try:
                data = json.loads(body.decode()) if body else {}
                lat = data.get("lat")
                lon = data.get("lon")
                svc = LocationService()
                coord_str = f"{lat} {lon}"
                loc, res, reported = svc.spoof_device_location(coord_str)
                self.wfile.write(json.dumps({
                    "success": res.success,
                    "message": res.message,
                    "reported": reported.model_dump() if reported else None
                }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        if parsed.path == "/api/reset":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            try:
                svc = LocationService()
                res = svc.stop_spoofing()
                self.wfile.write(json.dumps({"success": res.success, "message": res.message}).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return

        self.send_response(404)
        self.end_headers()


def start_server(port: int = 3000, open_browser: bool = True):
    """Start local web server serving React Flat Design frontend."""
    if not DIST_DIR.exists():
        print(f"Error: Web distribution directory not found at '{DIST_DIR}'.")
        print("Please run 'npm run build' inside the web directory first.")
        sys.exit(1)

    # Find available port
    for p in range(port, port + 20):
        try:
            httpd = socketserver.TCPServer(("", p), LocSpoofWebHandler)
            port = p
            break
        except OSError:
            continue
    else:
        print("Error: Could not bind to an available port.")
        sys.exit(1)

    url = f"http://localhost:{port}"
    print("=" * 64)
    print("  LOCSPOOF WEB GUI - Universal GPS Spoofer (Flat Design)")
    print(f"  Live Server: {url}")
    print("  Press Ctrl+C to stop.")
    print("=" * 64)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping LocSpoof Web server...")
        httpd.shutdown()


def run_gui():
    start_server(port=3000, open_browser=True)


if __name__ == "__main__":
    run_gui()
