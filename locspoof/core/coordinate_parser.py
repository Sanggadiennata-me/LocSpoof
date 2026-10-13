"""
Robust Coordinate Parser for locspoof.
Parses Decimal Degrees, DMS (Degrees Minutes Seconds), and alternative notation formats.
Handles cardinal directions (N, S, E, W) and enforces WGS84 geographic boundaries.
"""

import re
from typing import List, Optional, Tuple

from locspoof.core.exceptions import ValidationError
from locspoof.core.models import Coordinates


# Regex patterns for various coordinate notations
# Matches DMS like: 55°33'15.3"N or 6°12'10.2"S or 106°49'35.8"E
# Allows unicode degree/minute/second variants (° ' " ′ ″ ’ ”)
DMS_REGEX = re.compile(
    r"""(?P<deg>\d{1,3})[\s°d*]?\s*
        (?P<min>\d{1,2})[\s'′m]?\s*
        (?P<sec>\d{1,2}(?:\.\d+)?)[\s"″s]?\s*
        (?P<hemi>[NSEWnsew])""",
    re.VERBOSE,
)

# Alternative space-separated DMS: 55 33 15.3 N
DMS_SPACE_REGEX = re.compile(
    r"""(?P<deg>\d{1,3})\s+
        (?P<min>\d{1,2})\s+
        (?P<sec>\d{1,2}(?:\.\d+)?)\s*
        (?P<hemi>[NSEWnsew])""",
    re.VERBOSE,
)

# Decimal with optional cardinal letter: 55.554250 N or 6.2088S or -6.2088
DECIMAL_CARDINAL_REGEX = re.compile(
    r"^(?P<sign>[+-])?(?P<val>\d+(?:\.\d+)?)\s*(?P<hemi>[NSEWnsew])?$"
)


def _dms_to_decimal(deg: float, minutes: float, seconds: float, hemi: str) -> float:
    """Convert degrees, minutes, seconds and hemisphere letter into signed decimal degrees."""
    dec = float(deg) + (float(minutes) / 60.0) + (float(seconds) / 3600.0)
    hemi_upper = hemi.upper()
    if hemi_upper in ("S", "W"):
        dec = -dec
    return round(dec, 6)


def parse_single_coordinate(token: str, expected_type: Optional[str] = None) -> Tuple[float, str]:
    """
    Parse a single latitude or longitude component from token.
    Returns (decimal_value, hemisphere_or_type).
    """
    token = token.strip()

    # 1. Try standard DMS regex
    m = DMS_REGEX.search(token)
    if m:
        d = float(m.group("deg"))
        mn = float(m.group("min"))
        s = float(m.group("sec"))
        h = m.group("hemi").upper()
        return _dms_to_decimal(d, mn, s, h), h

    # 2. Try space DMS regex
    m = DMS_SPACE_REGEX.search(token)
    if m:
        d = float(m.group("deg"))
        mn = float(m.group("min"))
        s = float(m.group("sec"))
        h = m.group("hemi").upper()
        return _dms_to_decimal(d, mn, s, h), h

    # 3. Try decimal with cardinal or sign
    m = DECIMAL_CARDINAL_REGEX.match(token)
    if m:
        val = float(m.group("val"))
        if m.group("sign") == "-":
            val = -val
        h = m.group("hemi")
        if h:
            h = h.upper()
            if h in ("S", "W"):
                val = -abs(val)
            elif h in ("N", "E"):
                val = abs(val)
            return round(val, 6), h
        return round(val, 6), expected_type or "DECIMAL"

    raise ValueError(f"Unrecognized coordinate format: '{token}'")


def parse_coordinates(raw_input: str) -> Coordinates:
    """
    Parse user-provided coordinate string into a validated Coordinates model.
    
    Supports:
      - '55°33\'15.3"N 55°45\'56.2"E'
      - '6°12\'10.2"S 106°49\'35.8"E'
      - '55 33 15.3 N 55 45 56.2 E'
      - '55.554250 55.765611'
      - '-6.2088, 106.8456'
      - '55.554250N 55.765611E'
    """
    # Strip any enclosing parentheses, brackets, or quotes
    cleaned = raw_input.strip()
    cleaned = re.sub(r"^[(\[{'\"\s]+", "", cleaned)
    cleaned = re.sub(r"[)\]}'\"\s]+$", "", cleaned)
    # Normalize escaped quotes from shell
    cleaned = cleaned.replace(r'\"', '"').replace(r"\'", "'")

    if not cleaned:
        raise ValidationError(
            message="Coordinates input cannot be empty.",
            suggestion="Provide coordinates like '(0°27\\'18.2\"S 111°47\\'16.1\"E)' or '55.554250 55.765611'.",
        )

    # First attempt: Check for DMS patterns with N/S and E/W
    dms_matches = list(DMS_REGEX.finditer(cleaned))
    if len(dms_matches) >= 2:
        lat = None
        lon = None
        for m in dms_matches:
            val, hemi = _dms_to_decimal(
                m.group("deg"), m.group("min"), m.group("sec"), m.group("hemi")
            ), m.group("hemi").upper()
            if hemi in ("N", "S"):
                lat = val
            elif hemi in ("E", "W"):
                lon = val
        if lat is not None and lon is not None:
            return Coordinates(latitude=lat, longitude=lon)

    # Second attempt: Space-separated DMS patterns (e.g. "55 33 15.3 N 55 45 56.2 E")
    dms_space_matches = list(DMS_SPACE_REGEX.finditer(cleaned))
    if len(dms_space_matches) >= 2:
        lat = None
        lon = None
        for m in dms_space_matches:
            val, hemi = _dms_to_decimal(
                m.group("deg"), m.group("min"), m.group("sec"), m.group("hemi")
            ), m.group("hemi").upper()
            if hemi in ("N", "S"):
                lat = val
            elif hemi in ("E", "W"):
                lon = val
        if lat is not None and lon is not None:
            return Coordinates(latitude=lat, longitude=lon)

    # Third attempt: Decimal coordinates split by comma or whitespace
    # Replace comma with space if present
    normalized = cleaned.replace(",", " ")
    tokens = normalized.split()

    if len(tokens) == 2:
        try:
            val1, h1 = parse_single_coordinate(tokens[0], "LAT")
            val2, h2 = parse_single_coordinate(tokens[1], "LON")

            lat = None
            lon = None

            # Handle hemisphere associations if provided
            if h1 in ("N", "S") and h2 in ("E", "W"):
                lat, lon = val1, val2
            elif h1 in ("E", "W") and h2 in ("N", "S"):
                lon, lat = val1, val2
            else:
                # Default order: Latitude first, Longitude second
                lat, lon = val1, val2

            return Coordinates(latitude=lat, longitude=lon)
        except Exception as exc:
            pass

    # Fourth attempt: 8 tokens for space DMS (e.g. 55 33 15.3 N 55 45 56.2 E)
    if len(tokens) == 8:
        part1 = " ".join(tokens[0:4])
        part2 = " ".join(tokens[4:8])
        try:
            val1, h1 = parse_single_coordinate(part1)
            val2, h2 = parse_single_coordinate(part2)
            if h1 in ("N", "S") and h2 in ("E", "W"):
                return Coordinates(latitude=val1, longitude=val2)
            elif h1 in ("E", "W") and h2 in ("N", "S"):
                return Coordinates(latitude=val2, longitude=val1)
            return Coordinates(latitude=val1, longitude=val2)
        except Exception:
            pass

    # If parsing failed completely, raise human-readable ValidationError
    raise ValidationError(
        message=f"Could not parse coordinates from: '{raw_input}'",
        detail="The coordinate format did not match recognized Decimal Degrees or DMS conventions.",
        suggestion=(
            "Supported formats include:\n"
            "  - DMS: 55°33'15.3\"N 55°45'56.2\"E\n"
            "  - DMS South/West: 6°12'10.2\"S 106°49'35.8\"E\n"
            "  - Space DMS: 55 33 15.3 N 55 45 56.2 E\n"
            "  - Decimal: 55.554250 55.765611\n"
            "  - Signed Decimal: -6.2088 106.8456"
        ),
    )
