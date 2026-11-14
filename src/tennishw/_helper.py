"""Private helpers that turn tennisabstract.com Career JS text into a data frame."""

import json
import re


def _format_player_name(name):
    """Turn 'serena williams' / 'Serena Williams' / 'SerenaWilliams' into 'SerenaWilliams'."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Player name must be a non-empty string, e.g. 'Serena Williams'.")
    pieces = re.split(r"[^A-Za-z]+", name.strip())
    return "".join(p[0].upper() + p[1:] for p in pieces if p)

_MATRIX_PATTERN = re.compile(r"var\s+morematchmx\s*=\s*(\[\s*\[.*?\]\s*\])", re.DOTALL)


def _parse_matches_js(js_text):
    """Extract the list of match records stored in `var morematchmx = [...]`."""
    match = _MATRIX_PATTERN.search(js_text)
    if match is None:
        raise ValueError("Could not find 'morematchmx' match data in the JS content.")
    return json.loads(match.group(1))

OPP_AGE_OR_DOB = 16  # position of opponent's birth date (female) or age (male)


def _is_female_format(records):
    """Female files store opponent DOB (YYYYMMDD); male files store opponent age (float)."""
    values = [r[OPP_AGE_OR_DOB] for r in records if r[OPP_AGE_OR_DOB]]
    return bool(values) and all(re.fullmatch(r"\d{8}", v) for v in values)