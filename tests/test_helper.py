"""Tests for the private helpers in tennishw._helper (no network access)."""

from pathlib import Path

import pytest

from tennishw._helper import _format_player_name, _parse_matches_js

FAKE_DATA = Path(__file__).parent / "fake_data"


@pytest.fixture
def female_js():
    return (FAKE_DATA / "FemalePlayerCareer.js").read_text()


@pytest.fixture
def male_js():
    return (FAKE_DATA / "MalePlayerCareer.js").read_text()


# ---- name formatting ----

@pytest.mark.parametrize("raw", ["serena williams", "Serena Williams",
                                 "SerenaWilliams", "  serena   williams "])
def test_format_player_name_variants(raw):
    assert _format_player_name(raw) == "SerenaWilliams"


def test_format_player_name_hyphen():
    assert _format_player_name("jo-wilfried tsonga") == "JoWilfriedTsonga"


@pytest.mark.parametrize("bad", ["", "   ", None, 42])
def test_format_player_name_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        _format_player_name(bad)


# ---- extracting match records from JS ----

def test_parse_matches_js_female(female_js):
    records = _parse_matches_js(female_js)
    assert len(records) == 3
    assert records[0][11] == "Anne Miller"


def test_parse_matches_js_male(male_js):
    records = _parse_matches_js(male_js)
    assert len(records) == 3
    assert records[2][4] == "W"


def test_parse_matches_js_missing_variable():
    with pytest.raises(ValueError, match="morematchmx"):
        _parse_matches_js("var somethingelse = 1;")