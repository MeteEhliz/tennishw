"""Tests for the private helpers in tennishw._helper (no network access)."""

from pathlib import Path

import pandas as pd
import pytest

from tennishw._helper import (
    _format_player_name,
    _is_female_format,
    _parse_dob,
    _parse_matches_js,
    _records_to_frame,
)


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
        
# ---- female vs male detection ----

def test_female_vs_male_detection(female_js, male_js):
    assert _is_female_format(_parse_matches_js(female_js))
    assert not _is_female_format(_parse_matches_js(male_js))
    
# ---- building the data frame ----

SERENA_DOB = pd.Timestamp("1981-09-26")
RAFA_DOB = pd.Timestamp("1986-06-03")
EXPECTED_COLUMNS = ["date", "tournament", "surface", "result", "opponent",
                    "player_age", "opponent_age", "age_diff"]


def test_female_frame_ages(female_js):
    df = _records_to_frame(_parse_matches_js(female_js), SERENA_DOB)
    assert list(df.columns) == EXPECTED_COLUMNS
    first = df.iloc[0]
    assert first["opponent"] == "Anne Miller"
    assert first["player_age"] == pytest.approx(14.09, abs=0.01)
    assert first["opponent_age"] == pytest.approx(18.78, abs=0.01)
    assert first["age_diff"] == pytest.approx(14.09 - 18.78, abs=0.02)


def test_male_frame_uses_given_opponent_age(male_js):
    df = _records_to_frame(_parse_matches_js(male_js), RAFA_DOB)
    assert df["opponent_age"].tolist() == pytest.approx(
        [22.264202601, 24.2902121834, 18.7597535934])
    assert df["player_age"].iloc[0] == pytest.approx(15.27, abs=0.01)


def test_frame_results_and_order(male_js):
    df = _records_to_frame(_parse_matches_js(male_js), RAFA_DOB)
    assert set(df["result"]) <= {"W", "L"}
    assert df["date"].is_monotonic_increasing


def test_frame_drops_missing_opponent_age(male_js):
    records = _parse_matches_js(male_js)
    records[0][16] = ""
    df = _records_to_frame(records, RAFA_DOB)
    assert len(df) == 2
    assert df["opponent_age"].notna().all()
    
# ---- player date of birth ----

def test_parse_dob():
    page = "var fullname = 'Serena Williams';\nvar dob = 19810926;\n"
    assert _parse_dob(page) == SERENA_DOB
    assert _parse_dob("no dob here") is None