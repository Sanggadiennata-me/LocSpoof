import pytest
from locspoof.core.coordinate_parser import parse_coordinates
from locspoof.core.exceptions import ValidationError


def test_parse_dms_north_east():
    coords = parse_coordinates('55°33\'15.3"N 55°45\'56.2"E')
    assert abs(coords.latitude - 55.554250) < 0.0001
    assert abs(coords.longitude - 55.765611) < 0.0001


def test_parse_dms_with_quotes():
    coords = parse_coordinates('"55°33\'15.3"N 55°45\'56.2"E"')
    assert abs(coords.latitude - 55.554250) < 0.0001
    assert abs(coords.longitude - 55.765611) < 0.0001


def test_parse_dms_south_east():
    coords = parse_coordinates('6°12\'10.2"S 106°49\'35.8"E')
    assert abs(coords.latitude - (-6.202833)) < 0.0001
    assert abs(coords.longitude - 106.826611) < 0.0001


def test_parse_dms_space_separated():
    coords = parse_coordinates('55 33 15.3 N 55 45 56.2 E')
    assert abs(coords.latitude - 55.554250) < 0.0001
    assert abs(coords.longitude - 55.765611) < 0.0001


def test_parse_decimal_degrees():
    coords = parse_coordinates('55.554250 55.765611')
    assert coords.latitude == 55.554250
    assert coords.longitude == 55.765611


def test_parse_signed_decimal():
    coords = parse_coordinates('-6.2088, 106.8456')
    assert coords.latitude == -6.2088
    assert coords.longitude == 106.8456


def test_parse_dms_with_parentheses():
    # Test with user specific coordinate format: (0°27'18.2"S 111°47'16.1"E)
    coords = parse_coordinates('(0°27\'18.2"S 111°47\'16.1"E)')
    assert abs(coords.latitude - (-0.455056)) < 0.0001
    assert abs(coords.longitude - 111.787806) < 0.0001


def test_parse_invalid_coordinates_raises_error():
    with pytest.raises(ValidationError) as exc:
        parse_coordinates("invalid_not_coordinates")
    assert "Could not parse coordinates" in exc.value.message
