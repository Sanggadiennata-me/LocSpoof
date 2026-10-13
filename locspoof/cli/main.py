"""
Main CLI Application entrypoint for locspoof.
Refocused on Device-Level Android Location Spoofing as the primary interface.
Provides straightforward commands:
  locspoof <coordinates>
  locspoof start <coordinates>
  locspoof stop
  locspoof status
  locspoof devices
  locspoof reset
"""

import json
import sys
from typing import List, Optional
import typer
from rich.console import Console

from locspoof import __version__
from locspoof.cli.ui.formatter import (
    print_error,
    render_device_status,
    render_devices_list,
    render_doctor_report,
    render_spoof_active,
    render_status,
    render_verification_report,
)
from locspoof.config.storage import load_config, save_config
from locspoof.core.exceptions import LocSpoofError
from locspoof.core.models import ConsistencyLevel, Coordinates
from locspoof.core.service import LocationService
from locspoof.diagnostics.doctor import Doctor
from locspoof.providers.android.provider import AndroidProvider
from locspoof.providers.browser.provider import BrowserProvider
from locspoof.providers.network.provider import NetworkProvider
from locspoof.utils.logger import setup_logger

app = typer.Typer(
    name="locspoof",
    help="CLI Location Spoofer for Android Devices & Emulators.",
    no_args_is_help=False,
    add_completion=False,
)

# Optional secondary sub-command groups
android_app = typer.Typer(name="android", help="Advanced Android device & emulator controls.", no_args_is_help=True)
browser_app = typer.Typer(name="browser", help="Browser W3C Geolocation testing via CDP.", no_args_is_help=True)
network_app = typer.Typer(name="network", help="Network egress and IP-based geolocation testing.", no_args_is_help=True)
config_app = typer.Typer(name="config", help="Manage locspoof configuration settings.", no_args_is_help=True)

app.add_typer(android_app)
app.add_typer(browser_app)
app.add_typer(network_app)
app.add_typer(config_app)

console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]locspoof[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit(code=0)


def execute_spoof(coords_str: str, device_id: Optional[str] = None, live: bool = False):
    """Core action: Parse coordinates and apply mock location to Android device."""
    service = LocationService()
    try:
        loc, res, reported = service.spoof_device_location(coord_input=coords_str, device_id=device_id)

        target_dev = service.android_provider.get_target_device()
        dev_label = target_dev.serial if target_dev else (device_id or "Android Device")
        if target_dev and target_dev.model:
            dev_label += f" ({target_dev.model})"

        if res.success:
            render_spoof_active(
                target_coords=loc.coordinates,
                device_name=dev_label,
                provider_name="Android Mock Location",
                reported_coords=reported,
            )

            if live:
                import time
                console.print("[bold yellow]⚡ Live Spoofing Mode Active (1 Hz GPS Heartbeat).[/bold yellow]")
                console.print("[dim]Press Ctrl+C to terminate and restore real location...[/dim]\n")
                try:
                    while True:
                        time.sleep(1.0)
                        service.android_provider.apply_location(loc)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Interrupted by user. Restoring normal GPS...[/yellow]")
                    service.stop_spoofing(device_id=device_id)
                    console.print("[bold green]Normal device location restored.[/bold green]\n")
        else:
            print_error("Failed to apply mock location to device.", res.message)
            raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)
    except Exception as exc:
        print_error("Unexpected error during location spoofing.", str(exc))
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Show version and exit.", callback=version_callback, is_eager=True
    ),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Target specific Android device serial."),
    live: bool = typer.Option(False, "--live", "-l", help="Maintain continuous live location injection."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    debug: bool = typer.Option(False, "--debug", help="Enable internal debugging and tracing."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress informational messages."),
):
    """
    LocSpoof - Android Device Location Spoofer CLI.
    Run 'locspoof <coordinates>' to spoof device location.
    """
    if debug:
        setup_logger("debug")
    elif verbose:
        setup_logger("verbose")
    elif quiet:
        setup_logger("quiet")
    else:
        setup_logger("normal")

    # If no subcommand was called and arguments were provided to root CLI
    if ctx.invoked_subcommand is None:
        args = ctx.args
        if args:
            raw_input = " ".join(args)
            execute_spoof(raw_input, device_id=device, live=live)
        else:
            # If no args at all, print concise usage
            console.print("[bold cyan]LocSpoof - Android Location Spoofer CLI[/bold cyan]")
            console.print("\nUsage:")
            console.print("  [green]locspoof <coordinates>[/green]                 Spoof device location")
            console.print("  [green]locspoof status[/green]                        Show active spoofing status")
            console.print("  [green]locspoof stop[/green]                          Stop spoofing and restore real GPS")
            console.print("  [green]locspoof devices[/green]                       List connected Android devices")
            console.print("  [green]locspoof doctor[/green]                        Run environment diagnostics")
            console.print("\nExamples:")
            console.print("  locspoof 55°33'15.3\"N 55°45'56.2\"E")
            console.print("  locspoof 55.554250 55.765611")
            console.print("  locspoof \"6°12'10.2\"S 106°49'35.8\"E\"")
            console.print("  locspoof --device emulator-5554 -6.2088 106.8456\n")


# =========================================================================
# PRIMARY COMMANDS: start, stop, status, devices, reset, doctor
# =========================================================================

@app.command(name="start", help="Start mock location spoofing on Android device.")
def start_cmd(
    coordinates: List[str] = typer.Argument(..., help="Coordinates (DMS or Decimal)."),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Target specific device serial."),
    live: bool = typer.Option(False, "--live", "-l", help="Maintain continuous live location injection."),
):
    coord_input = " ".join(coordinates)
    execute_spoof(coord_input, device_id=device, live=live)


@app.command(name="paste", help="Paste raw coordinates interactively without shell quote escaping.")
def paste_cmd(
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Target specific device serial."),
    live: bool = typer.Option(False, "--live", "-l", help="Maintain continuous live location injection."),
):
    console.print("\n[bold cyan]📋 Paste Coordinates Mode[/bold cyan]")
    console.print("[dim]Paste your raw coordinates (e.g. from Google Maps) and press Enter:[/dim]\n")
    try:
        raw_input = input("Coordinates > ").strip()
        if not raw_input:
            console.print("[yellow]Empty input. Cancelled.[/yellow]\n")
            return
        execute_spoof(raw_input, device_id=device, live=live)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/yellow]\n")


@app.command(name="stop", help="Stop spoofing and restore device to normal location.")
def stop_cmd(
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Target specific device serial."),
):
    service = LocationService()
    try:
        res = service.stop_spoofing(device_id=device)
        console.print("\n[bold green]Location Spoofing Stopped:[/bold green]")
        console.print(f"  • Status  : Normal Location Restored")
        console.print(f"  • Message : {res.message}\n")
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)


@app.command(name="status", help="Show active spoofing target, reported device coordinates, and provider state.")
def status_cmd(
    as_json: bool = typer.Option(False, "--json", help="Output in JSON format."),
):
    service = LocationService()
    try:
        info = service.get_spoof_status()
        if as_json:
            out = {
                "target_location": info["target_location"].model_dump() if info["target_location"] else None,
                "reported_coordinates": info["reported_coordinates"].model_dump() if info["reported_coordinates"] else None,
                "mock_provider_status": info["mock_provider_status"],
                "device": info["device"].model_dump() if info["device"] else None,
                "spoofing_active": info["spoofing_active"],
            }
            console.print(json.dumps(out, indent=2, default=str))
        else:
            render_device_status(info)
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)


@app.command(name="devices", help="List connected Android physical devices and emulators.")
def devices_cmd():
    service = LocationService()
    try:
        devs = service.list_devices()
        render_devices_list(devs)
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)


@app.command(name="reset", help="Reset all mock providers and clear configuration state.")
def reset_cmd():
    service = LocationService()
    try:
        service.stop_spoofing()
        results = service.reset()
        console.print("\n[bold green]Cleanup & Reset Completed:[/bold green]")
        for prov_name, op in results.items():
            status_badge = "[green]OK[/green]" if op.success else "[red]FAIL[/red]"
            console.print(f"  • [bold]{prov_name.title()}[/bold]: {status_badge} - {op.message}")
        console.print()
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)


@app.command(name="doctor", help="Inspect Android ADB, devices, and runtime environment.")
def doctor_cmd():
    doctor = Doctor()
    report = doctor.run_diagnostics()
    render_doctor_report(report)
    if report.error_count > 0:
        raise typer.Exit(code=3)


@app.command(name="verify", help="Audit consistency between GPS, network IP, and timezone signals.")
def verify_cmd(
    strict: bool = typer.Option(False, "--strict", help="Return exit code 2 if mismatch detected."),
):
    service = LocationService()
    try:
        verification = service.verify()
        render_verification_report(verification)
        if strict and verification.consistency != ConsistencyLevel.MATCH:
            raise typer.Exit(code=2)
        elif verification.consistency == ConsistencyLevel.MISMATCH:
            raise typer.Exit(code=2)
    except typer.Exit:
        raise
    except LocSpoofError as exc:
        print_error(exc.message, exc.detail, exc.suggestion)
        raise typer.Exit(code=exc.exit_code)


# =========================================================================
# SECONDARY SUBCOMMANDS (BROWSER, NETWORK, CONFIG)
# =========================================================================

@browser_app.command(name="status")
def browser_status():
    provider = BrowserProvider()
    cap = provider.check_capability()
    console.print(f"\n[bold]Browser Provider Status:[/bold] {cap.status_summary}\n")


@browser_app.command(name="launch")
def browser_launch(
    url: Optional[str] = typer.Option(None, "--url", "-u"),
    lat: Optional[float] = typer.Option(None, "--lat"),
    lon: Optional[float] = typer.Option(None, "--lon"),
):
    provider = BrowserProvider()
    coords = Coordinates(latitude=lat, longitude=lon) if (lat is not None and lon is not None) else None
    res = provider.launch_browser(target_url=url, coords=coords)
    console.print(f"\n{res.message}\n")


@network_app.command(name="status")
def network_status():
    cfg = load_config()
    provider = NetworkProvider(proxy_url=cfg.network.proxy_url)
    sig = provider.get_current_signal()
    console.print("\n[bold cyan]Network Egress Status:[/bold cyan]")
    if sig.is_active and sig.coordinates:
        console.print(f"  • Public IP   : {sig.ip_address}")
        console.print(f"  • Location    : {sig.city or '-'}, {sig.country or '-'}")
        console.print(f"  • Timezone    : {sig.timezone_name or '-'}")
    else:
        console.print(f"  [yellow]Failed to resolve egress IP:[/yellow] {sig.error_message}")
    console.print()


@config_app.command(name="show")
def config_show():
    cfg = load_config()
    console.print(json.dumps(cfg.model_dump(), indent=2, default=str))


def run_app():
    """Entry point callable from console_scripts."""
    # Pre-process arguments to support shorthand: locspoof <coordinates>
    # If the first argument is not a registered command or option, rewrite to start
    registered_verbs = {
        "start", "paste", "stop", "status", "devices", "reset", "doctor", "verify",
        "android", "browser", "network", "config", "set",
        "--help", "-h", "--version", "-V",
    }
    raw_args = sys.argv[1:]
    if raw_args:
        first_token = raw_args[0]
        if first_token not in registered_verbs and not first_token.startswith("-"):
            # Insert 'start' as the command
            sys.argv.insert(1, "start")

    app()


if __name__ == "__main__":
    run_app()
