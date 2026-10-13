"""
Terminal output formatting using Rich.
Produces clean, professional security-tool style tables, panels, and badges.
"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from locspoof.core.models import (
    ConsistencyLevel,
    Coordinates,
    Location,
    LocationSignal,
    LocationVerification,
    ProviderCapability,
)
from locspoof.diagnostics.doctor import DoctorReport
from locspoof.providers.android.adb_client import AndroidDevice

console = Console()


def print_error(message: str, detail: Optional[str] = None, suggestion: Optional[str] = None) -> None:
    """Print human-readable error with detail and actionable suggestions."""
    err_text = Text()
    err_text.append("ERROR: ", style="bold red")
    err_text.append(f"{message}\n")

    if detail:
        err_text.append("\nDETAIL:\n", style="bold yellow")
        err_text.append(f"{detail}\n")

    if suggestion:
        err_text.append("\nSUGGESTION:\n", style="bold cyan")
        err_text.append(f"{suggestion}\n")

    console.print(Panel(err_text, border_style="red", title="LocSpoof Alert"))


def render_spoof_active(
    target_coords: Coordinates,
    device_name: str,
    provider_name: str = "Android Mock Location",
    reported_coords: Optional[Coordinates] = None,
) -> None:
    """
    Render confirmation that device location spoofing is active.
    """
    console.print()
    panel_text = Text()
    panel_text.append("Location Spoofing Active\n\n", style="bold green")

    panel_text.append("Target:\n", style="bold")
    panel_text.append(f"{target_coords.latitude:.6f}, {target_coords.longitude:.6f}\n\n", style="cyan")

    panel_text.append("Device:\n", style="bold")
    panel_text.append(f"{device_name}\n\n", style="yellow")

    panel_text.append("Provider:\n", style="bold")
    panel_text.append(f"{provider_name}\n\n", style="magenta")

    if reported_coords:
        panel_text.append("Device Reported:\n", style="bold")
        panel_text.append(f"{reported_coords.latitude:.6f}, {reported_coords.longitude:.6f}\n\n", style="green")

    panel_text.append("Status:\n", style="bold")
    panel_text.append("ACTIVE", style="bold green")

    console.print(Panel(panel_text, border_style="green", title="LocSpoof"))
    console.print()


def render_device_status(status_info: Dict) -> None:
    """
    Render Android device location spoofing status.
    """
    active_loc: Optional[Location] = status_info.get("target_location")
    reported: Optional[Coordinates] = status_info.get("reported_coordinates")
    target_dev: Optional[AndroidDevice] = status_info.get("device")
    mock_status: str = status_info.get("mock_provider_status", "INACTIVE")
    is_active: bool = status_info.get("spoofing_active", False)

    console.print()
    console.rule("[bold cyan]ANDROID LOCATION STATUS[/bold cyan]")
    console.print()

    table = Table(show_header=False, box=None)
    table.add_column("Property", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Real/Physical Location", "[dim]UNKNOWN / unavailable[/dim]")

    if active_loc:
        table.add_row("Spoofed Target Location", f"{active_loc.latitude:.6f}, {active_loc.longitude:.6f}")
    else:
        table.add_row("Spoofed Target Location", "[yellow]None (Normal Location Mode)[/yellow]")

    if reported:
        table.add_row("Device Reported Location", f"[bold green]{reported.latitude:.6f}, {reported.longitude:.6f}[/bold green]")
    else:
        table.add_row("Device Reported Location", "[dim]Not reported / Query pending[/dim]")

    status_color = "bold green" if is_active else "dim yellow"
    table.add_row("Mock Provider", f"[{status_color}]{mock_status}[/{status_color}]")

    if target_dev:
        dev_label = f"connected ({target_dev.serial})"
        if target_dev.model:
            dev_label += f" [{target_dev.model}]"
        table.add_row("Device", dev_label)
    else:
        table.add_row("Device", "[red]NO DEVICE CONNECTED[/red]")

    table.add_row("Provider", "Android Mock Location / Emulator GNSS")

    console.print(Panel(table, border_style="blue", title="Device State"))

    if active_loc and reported:
        from locspoof.verification.math import haversine_distance_km
        delta = haversine_distance_km(active_loc.coordinates, reported)
        if delta < 0.05:
            console.print("[bold green]✓ VERIFIED:[/bold green] Device location successfully matches target coordinates.")
        else:
            console.print(f"[bold yellow]! NOTICE:[/bold yellow] Device reported location deviates by {delta:.2f} km from target.")
    console.print()


def render_devices_list(devices: List[AndroidDevice]) -> None:
    """
    Render list of connected Android devices with detailed capabilities.
    """
    console.print()
    console.rule("[bold cyan]ATTACHED ANDROID DEVICES[/bold cyan]")
    console.print()

    if not devices:
        console.print("[yellow]No Android devices or emulators found.[/yellow]")
        console.print("Suggestion: Launch an Android Virtual Device (AVD) or connect a device via USB with Debugging enabled.\n")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Device Serial", style="bold")
    table.add_column("Type")
    table.add_column("Model")
    table.add_column("Android OS")
    table.add_column("ADB State")
    table.add_column("Mock Location Support")

    for d in devices:
        kind = "Emulator" if d.is_emulator else "Physical Device"
        os_str = f"Android {d.android_version} (API {d.sdk_version})" if d.android_version else "-"
        state_style = "[green]connected[/green]" if d.state == "device" else f"[yellow]{d.state}[/yellow]"
        mock_style = "[green]available[/green]" if d.is_emulator else "[yellow]app required[/yellow]"

        table.add_row(
            d.serial,
            kind,
            d.model or "-",
            os_str,
            state_style,
            d.mock_location_status or mock_style,
        )

    console.print(table)
    console.print()


def render_status(status_data: Dict) -> None:
    """Render comprehensive location status."""
    configured: Optional[Location] = status_data.get("configured_location")
    capabilities: List[ProviderCapability] = status_data.get("capabilities", [])
    signals: List[LocationSignal] = status_data.get("signals", [])
    verification: Optional[LocationVerification] = status_data.get("verification")

    console.print()
    console.rule("[bold cyan]LOCATION STATUS[/bold cyan]")
    console.print()

    config_table = Table(title="Configured Target Location", show_header=False, box=None)
    config_table.add_column("Field", style="bold")
    config_table.add_column("Value", style="cyan")

    if configured:
        config_table.add_row("Name / City", str(configured.name or "-"))
        config_table.add_row("Latitude", f"{configured.latitude:.6f}")
        config_table.add_row("Longitude", f"{configured.longitude:.6f}")
        config_table.add_row("Altitude", f"{configured.altitude} m" if configured.altitude is not None else "-")
        config_table.add_row("Accuracy", f"{configured.accuracy} m" if configured.accuracy is not None else "-")
        config_table.add_row("Source", configured.source.value)
    else:
        config_table.add_row("Status", "[yellow]No location configured. Use 'locspoof <coordinates>' to set coordinates.[/yellow]")

    console.print(Panel(config_table, border_style="blue", title="Target Anchor"))
    console.print()

    prov_table = Table(title="Provider Environments", show_header=True, header_style="bold magenta")
    prov_table.add_column("Provider", style="bold")
    prov_table.add_column("Status")
    prov_table.add_column("Details")

    for cap in capabilities:
        status_style = "[green]AVAILABLE[/green]" if cap.available else "[yellow]UNAVAILABLE[/yellow]"
        prov_table.add_row(
            cap.name.title(),
            f"{status_style} ({cap.status_summary})",
            cap.suggestion or "-",
        )

    console.print(prov_table)
    console.print()

    if signals:
        sig_table = Table(title="Observed Signals", show_header=True, header_style="bold green")
        sig_table.add_column("Source", style="bold")
        sig_table.add_column("Perceived Location")
        sig_table.add_column("Coordinates / Value")
        sig_table.add_column("State")

        for sig in signals:
            coords_str = f"{sig.coordinates.latitude:.4f}, {sig.coordinates.longitude:.4f}" if sig.coordinates else "-"
            loc_label = sig.city or sig.country or (sig.coordinates and "Coordinates Available") or "-"
            if sig.source.value == "network_ip" and sig.ip_address:
                coords_str += f" ({sig.ip_address})"

            state_style = "[green]ACTIVE[/green]" if sig.is_active else "[dim]INACTIVE[/dim]"
            sig_table.add_row(sig.source_name, str(loc_label), coords_str, state_style)

        console.print(sig_table)
        console.print()


def render_doctor_report(report: DoctorReport) -> None:
    """Render doctor diagnostic results."""
    console.print()
    console.rule("[bold cyan]LOCSPOOF SYSTEM & ENVIRONMENT DIAGNOSTICS[/bold cyan]")
    console.print()

    for item in report.items:
        if item.status == "OK":
            badge = "[bold green][OK]   [/bold green]"
        elif item.status == "WARN":
            badge = "[bold yellow][WARN] [/bold yellow]"
        else:
            badge = "[bold red][ERROR][/bold red]"

        console.print(f"{badge} [bold]{item.name:<24}[/bold] {item.message}")
        if item.suggestion:
            console.print(f"         [dim]↳ Suggestion: {item.suggestion}[/dim]")

    console.print()
    summary_text = (
        f"Diagnostics Result: [green]{report.passed_count} Passed[/green], "
        f"[yellow]{report.warn_count} Warnings[/yellow], "
        f"[red]{report.error_count} Errors[/red]"
    )
    console.print(Panel(summary_text, border_style="cyan" if report.is_healthy else "red"))
    console.print()


def render_verification_report(verification: LocationVerification) -> None:
    """Render in-depth multi-signal verification report."""
    console.print()
    console.rule("[bold cyan]MULTI-SIGNAL LOCATION AUDIT & VERIFICATION REPORT[/bold cyan]")
    console.print()

    table = Table(title="Signal Matrix", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="bold")
    table.add_column("Resolved Location")
    table.add_column("Coordinates / Identifier")
    table.add_column("Timezone / Extra")

    for s in verification.signals:
        coords = f"{s.coordinates.latitude:.6f}, {s.coordinates.longitude:.6f}" if s.coordinates else "-"
        loc = f"{s.city or '-'}, {s.country or '-'}"
        extra = s.timezone_name or (s.ip_address and f"IP: {s.ip_address}") or "-"
        table.add_row(s.source_name, loc, coords, extra)

    console.print(table)
    console.print()

    level_color = {
        ConsistencyLevel.MATCH: "green",
        ConsistencyLevel.WARNING: "yellow",
        ConsistencyLevel.MISMATCH: "red",
        ConsistencyLevel.UNKNOWN: "dim",
    }.get(verification.consistency, "white")

    console.print(
        Panel(
            f"Overall Consistency: [bold {level_color}]{verification.consistency.value}[/bold {level_color}]\n"
            f"Consistency Trust Score: [bold]{verification.consistency_score}/100[/bold]",
            border_style=level_color,
            title="Verification Summary",
        )
    )

    if verification.mismatches:
        console.print("\n[bold red]Detected Signal Inconsistencies & Leaks:[/bold red]")
        for idx, m in enumerate(verification.mismatches, 1):
            sev_badge = f"[{m.severity}]"
            console.print(f"  {idx}. [bold yellow]{sev_badge}[/bold yellow] {m.description}")

    if verification.recommendations:
        console.print("\n[bold cyan]Actionable Recommendations:[/bold cyan]")
        for rec in verification.recommendations:
            console.print(f"  [cyan]•[/cyan] {rec}")
    console.print()
