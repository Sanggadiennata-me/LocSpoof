"""
Verification Engine for locspoof.
Cross-references multi-source location signals (GPS, Browser, IP, Timezone)
and detects discrepancies, leakage, and spoofing indicators.
"""

import time
from typing import List, Optional

from locspoof.core.models import (
    ConsistencyLevel,
    Coordinates,
    LocationMismatch,
    LocationSignal,
    LocationSource,
    LocationVerification,
)
from locspoof.verification.math import haversine_distance_km


class VerificationEngine:
    """
    Engine responsible for auditing multi-signal location consistency.
    """

    def __init__(self, distance_threshold_km: float = 75.0):
        self.distance_threshold_km = distance_threshold_km

    def verify(
        self,
        signals: List[LocationSignal],
        anchor_coords: Optional[Coordinates] = None,
    ) -> LocationVerification:
        """
        Verify consistency across provided location signals.
        """
        active_signals = [s for s in signals if s.is_active and s.coordinates is not None]
        mismatches: List[LocationMismatch] = []
        recommendations: List[str] = []
        score = 100

        # Determine reference anchor: explicitly given anchor, or the first GPS/Config signal
        anchor = anchor_coords
        anchor_name = "Configured Target"
        if not anchor:
            for s in active_signals:
                if s.source in (LocationSource.CONFIG, LocationSource.GPS, LocationSource.ANDROID, LocationSource.EMULATOR):
                    anchor = s.coordinates
                    anchor_name = s.source_name
                    break

        if not anchor and active_signals:
            anchor = active_signals[0].coordinates
            anchor_name = active_signals[0].source_name

        if not anchor:
            return LocationVerification(
                consistency=ConsistencyLevel.UNKNOWN,
                consistency_score=0,
                signals=signals,
                mismatches=[
                    LocationMismatch(
                        signal_a="System",
                        signal_b="None",
                        description="No valid location coordinates found among active signals.",
                        severity="CRITICAL",
                    )
                ],
                recommendations=["Configure a target location with 'locspoof set --lat <LAT> --lon <LON>'."],
            )

        # 1. Compare active signals against the anchor
        for sig in active_signals:
            if sig.coordinates == anchor:
                continue

            dist = haversine_distance_km(anchor, sig.coordinates)

            if sig.source == LocationSource.BROWSER:
                # Browser should strictly match target GPS in browser testing
                if dist > 1.0:  # More than 1km discrepancy
                    score -= 30
                    mismatches.append(
                        LocationMismatch(
                            signal_a=anchor_name,
                            signal_b=f"Browser ({sig.source_name})",
                            distance_km=dist,
                            description=f"Browser geolocation deviates from {anchor_name} by {dist:,.1f} km.",
                            severity="CRITICAL" if dist > 50 else "WARNING",
                        )
                    )
                    recommendations.append(
                        f"Re-synchronize browser geolocation override with 'locspoof browser set'."
                    )

            elif sig.source == LocationSource.NETWORK_IP:
                # Public IP location difference
                if dist > self.distance_threshold_km:
                    score -= 40
                    mismatches.append(
                        LocationMismatch(
                            signal_a=anchor_name,
                            signal_b=f"Egress IP ({sig.ip_address or 'Unknown IP'})",
                            distance_km=dist,
                            description=(
                                f"Egress IP location ({sig.city or 'Unknown'}, {sig.country or ''}) "
                                f"is {dist:,.1f} km away from {anchor_name}."
                            ),
                            severity="CRITICAL" if dist > 500 else "WARNING",
                        )
                    )
                    recommendations.append(
                        "Public egress IP does not match simulated GPS coordinates. "
                        "Configure a localized proxy or tunnel to align network layer: 'locspoof network proxy --url <PROXY>'."
                    )

            elif sig.source in (LocationSource.ANDROID, LocationSource.EMULATOR, LocationSource.GPS):
                if dist > 5.0:
                    score -= 30
                    mismatches.append(
                        LocationMismatch(
                            signal_a=anchor_name,
                            signal_b=sig.source_name,
                            distance_km=dist,
                            description=f"Android/Emulator GPS differs by {dist:,.1f} km from {anchor_name}.",
                            severity="WARNING",
                        )
                    )
                    recommendations.append(
                        "Synchronize Android device coordinates via 'locspoof android set'."
                    )

        # 2. Check Timezone discrepancy if available
        # Find network/IP signal or system timezone
        ip_signal = next((s for s in signals if s.source == LocationSource.NETWORK_IP), None)
        system_tz = time.tzname[0] if time.tzname else None
        if ip_signal and ip_signal.timezone_name:
            # Check if host timezone conflicts
            if system_tz and system_tz.upper() not in ip_signal.timezone_name.upper():
                score -= 10
                mismatches.append(
                    LocationMismatch(
                        signal_a=f"System Timezone ({system_tz})",
                        signal_b=f"IP Timezone ({ip_signal.timezone_name})",
                        description=f"System timezone '{system_tz}' differs from egress IP timezone '{ip_signal.timezone_name}'.",
                        severity="INFO",
                    )
                )
                recommendations.append(
                    "Consider setting matching TZ environment variable when testing timezone-sensitive web applications."
                )

        score = max(0, min(100, score))

        if score >= 90:
            level = ConsistencyLevel.MATCH
        elif score >= 50:
            level = ConsistencyLevel.WARNING
        else:
            level = ConsistencyLevel.MISMATCH

        return LocationVerification(
            consistency=level,
            consistency_score=score,
            signals=signals,
            mismatches=mismatches,
            recommendations=recommendations,
        )
