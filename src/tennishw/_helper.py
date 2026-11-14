"""Private helpers that turn tennisabstract.com Career JS text into a data frame."""

import json
import re

import pandas as pd

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

DAYS_PER_YEAR = 365.25


def _years_between(start, end):
    """Age in (fractional) years between two date columns."""
    return (end - start).dt.days / DAYS_PER_YEAR


def _opponent_age(raw, match_dates, female):
    """Opponent age at match time, from DOB (female files) or directly (male files)."""
    if female:
        dob = pd.to_datetime(raw, format="%Y%m%d", errors="coerce")
        return _years_between(dob, match_dates)
    return pd.to_numeric(raw, errors="coerce")

# positions of the fields we use in each match record
DATE, TOURNAMENT, SURFACE, RESULT, OPPONENT = 0, 1, 2, 4, 11


def _match_info(raw):
    """Descriptive columns: date, tournament, surface, result, opponent."""
    return pd.DataFrame({
        "date": pd.to_datetime(raw[DATE], format="%Y%m%d", errors="coerce"),
        "tournament": raw[TOURNAMENT],
        "surface": raw[SURFACE],
        "result": raw[RESULT],
        "opponent": raw[OPPONENT],
    })


def _records_to_frame(records, player_dob):
    """Build the clean data frame used for plotting from raw match records."""
    raw = pd.DataFrame([r[: OPP_AGE_OR_DOB + 1] for r in records])
    df = _match_info(raw)
    df["player_age"] = _years_between(pd.Series(player_dob, index=df.index), df["date"])
    df["opponent_age"] = _opponent_age(raw[OPP_AGE_OR_DOB], df["date"], _is_female_format(records))
    df["age_diff"] = df["player_age"] - df["opponent_age"]
    df = df[df["result"].isin(["W", "L"])].dropna(subset=["player_age", "opponent_age"])
    return df.sort_values("date").reset_index(drop=True)