"""Public function to download and clean a player's career matches."""

import pandas as pd
import requests

from ._helper import (
    _format_player_name,
    _is_female_format,
    _parse_dob,
    _parse_matches_js,
    _records_to_frame,
)

BASE_URL = "https://www.tennisabstract.com"
_TIMEOUT = 30


def _fetch_text(url):
    """GET a URL and return its text, or None if the page does not exist."""
    response = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "tennishw"})
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def _fetch_career_js(slug, display_name):
    """Download the Career JS file for a player slug like 'SerenaWilliams'."""
    js_text = _fetch_text(f"{BASE_URL}/jsmatches/{slug}Career.js")
    if js_text is None or "morematchmx" not in js_text:
        raise ValueError(
            f"No player named '{display_name}' was found on tennisabstract.com. "
            "Check the spelling, e.g. 'Serena Williams' or 'Rafael Nadal'."
        )
    return js_text


def _fetch_player_dob(slug, female):
    """Read the player's date of birth from their tennisabstract.com profile page."""
    page = "wplayer.cgi" if female else "player.cgi"
    page_text = _fetch_text(f"{BASE_URL}/cgi-bin/{page}?p={slug}")
    dob = _parse_dob(page_text) if page_text else None
    if dob is None:
        raise ValueError(f"No date of birth found for '{slug}'; pass player_dob='YYYY-MM-DD'.")
    return dob


def get_career_data(player_name, player_dob=None):
    """Get a player's career matches as a clean data frame ready for plotting.

    player_name: e.g. "serena williams", "Serena Williams" or "SerenaWilliams".
    player_dob: optional date of birth; looked up on tennisabstract.com if omitted.
    Returns one row per match: date, tournament, surface, result ("W"/"L"),
    opponent, player_age, opponent_age, age_diff (player_age - opponent_age).
    Raises ValueError if the player is not found on tennisabstract.com.
    """
    slug = _format_player_name(player_name)
    records = _parse_matches_js(_fetch_career_js(slug, player_name))
    if player_dob is None:
        player_dob = _fetch_player_dob(slug, _is_female_format(records))
    return _records_to_frame(records, pd.to_datetime(player_dob))