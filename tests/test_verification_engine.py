import pytest
from locspoof.core.models import (
    ConsistencyLevel,
    Coordinates,
    LocationMismatch,
    LocationSignal,
    LocationSource,
)
from locspoof.verification.engine import VerificationEngine
from locspoof.verification.math import haversine_distance_km


def test_haversine_distance():
    # Jakarta (-6.2088, 106.8456) to Bandung (-6.9175, 107.6191) is ~120 km
    c1 = Coordinates(latitude=-6.2088, longitude=106.8456)
    c2 = Coordinates(latitude=-6.9175, longitude=107.6191)
    dist = haversine_distance_km(c1, c2)
    assert 110 < dist < 140


def test_verification_perfect_match():
    engine = VerificationEngine(distance_threshold_km=50.0)
    anchor = Coordinates(latitude=-6.2088, longitude=106.8456)

    signals = [
        LocationSignal(
            source=LocationSource.GPS,
            source_name="GPS Hardware",
            coordinates=anchor,
            city="Jakarta",
        ),
        LocationSignal(
            source=LocationSource.BROWSER,
            source_name="Browser Geolocation",
            coordinates=anchor,
            city="Jakarta",
        ),
        LocationSignal(
            source=LocationSource.NETWORK_IP,
            source_name="Public IP",
            coordinates=Coordinates(latitude=-6.2100, longitude=106.8500),  # ~1km away
            city="Jakarta",
            timezone_name="Asia/Jakarta",
        ),
    ]

    result = engine.verify(signals=signals, anchor_coords=anchor)
    assert result.consistency in (ConsistencyLevel.MATCH, ConsistencyLevel.WARNING)
    assert result.consistency_score >= 80
    assert len([m for m in result.mismatches if m.severity == "CRITICAL"]) == 0


def test_verification_severe_mismatch():
    engine = VerificationEngine(distance_threshold_km=50.0)
    jakarta_coords = Coordinates(latitude=-6.2088, longitude=106.8456)
    montreal_coords = Coordinates(latitude=45.5017, longitude=-73.5673)

    signals = [
        LocationSignal(
            source=LocationSource.GPS,
            source_name="GPS Hardware",
            coordinates=jakarta_coords,
            city="Jakarta",
        ),
        LocationSignal(
            source=LocationSource.NETWORK_IP,
            source_name="Public IP",
            coordinates=montreal_coords,
            city="Montreal",
            country="Canada",
            timezone_name="America/Toronto",
        ),
    ]

    result = engine.verify(signals=signals, anchor_coords=jakarta_coords)
    assert result.consistency in (ConsistencyLevel.WARNING, ConsistencyLevel.MISMATCH)
    assert any("Montreal" in m.description for m in result.mismatches)
    assert len(result.recommendations) > 0
