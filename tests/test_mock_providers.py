import pytest
from locspoof.core.models import Coordinates, Location, LocationSource
from locspoof.providers.mock.mock_providers import (
    MockBrowserProvider,
    MockGPSProvider,
    MockNetworkProvider,
)


def test_mock_gps_provider():
    p = MockGPSProvider()
    cap = p.check_capability()
    assert cap.available is True

    new_loc = Location(latitude=35.6762, longitude=139.6503, name="Tokyo")
    res = p.apply_location(new_loc)
    assert res.success is True

    sig = p.get_current_signal()
    assert sig.coordinates.latitude == 35.6762
    assert sig.coordinates.longitude == 139.6503

    p.reset()
    assert p.get_current_signal().coordinates is None


def test_mock_browser_provider():
    p = MockBrowserProvider()
    assert p.check_capability().available is True

    loc = Location(latitude=51.5074, longitude=-0.1278, name="London")
    res = p.apply_location(loc)
    assert res.success is True
    assert p.get_current_signal().coordinates.latitude == 51.5074


def test_mock_network_provider_refuses_direct_spoof():
    p = MockNetworkProvider()
    loc = Location(latitude=1.3521, longitude=103.8198, name="Singapore")
    res = p.apply_location(loc)
    # Crucial security rule: Cannot directly change IP location by spoofing GPS
    assert res.success is False
    assert "proxy" in res.message.lower()
