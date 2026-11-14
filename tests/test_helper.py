"""Tests for the private helpers in tennishw._helper (no network access)."""

import pytest

from tennishw._helper import _format_player_name


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