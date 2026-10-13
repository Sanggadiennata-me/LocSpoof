import pytest
from pydantic import ValidationError

from locspoof.core.models import Coordinates, Location, LocationSource


def test_valid_coordinates():
    c = Coordinates(latitude=-6.2088, longitude=106.8456, altitude=15.0, accuracy=5.0)
    assert c.latitude == -6.2088
    assert c.longitude == 106.8456
    assert c.altitude == 15.0
    assert c.accuracy == 5.0


def test_invalid_latitude():
    with pytest.raises(ValidationError):
        Coordinates(latitude=95.0, longitude=106.0)

    with pytest.raises(ValidationError):
        Coordinates(latitude=-91.0, longitude=106.0)


def test_invalid_longitude():
    with pytest.raises(ValidationError):
        Coordinates(latitude=0.0, longitude=185.0)

    with pytest.raises(ValidationError):
        Coordinates(latitude=0.0, longitude=-181.0)


def test_negative_accuracy():
    with pytest.raises(ValidationError):
        Coordinates(latitude=0.0, longitude=0.0, accuracy=-5.0)


def test_location_model():
    loc = Location(
        latitude=48.8566,
        longitude=2.3522,
        name="Paris",
        source=LocationSource.CONFIG,
    )
    assert loc.coordinates.latitude == 48.8566
    assert loc.coordinates.longitude == 2.3522
    assert loc.name == "Paris"
