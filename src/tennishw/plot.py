"""Public function to draw the NYT-style age-gap scatter plot."""

import matplotlib.pyplot as plt

_COLORS = {"W": "#2a7ab9", "L": "#d95f43"}
_LABELS = {"W": "Win", "L": "Loss"}
_REQUIRED = {"player_age", "age_diff", "result"}


def _check_columns(career_df):
    """Make sure the data frame came from get_career_data()."""
    missing = _REQUIRED - set(career_df.columns)
    if missing:
        raise ValueError(f"Data frame is missing columns {sorted(missing)}; "
                         "create it with tennishw.get_career_data().")


def _style_axes(ax, title):
    """Add axis labels, the zero reference line, legend and title."""
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Player's age (years)")
    ax.set_ylabel("Player's age minus opponent's age (years)")
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)


def plot_age_gap(career_df, title=None, ax=None):
    """Scatter plot of player age vs. age difference, colored by win/loss.

    career_df: data frame returned by get_career_data().
    title: optional plot title. ax: optional matplotlib Axes to draw on.
    Returns the matplotlib Axes.
    """
    _check_columns(career_df)
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5.5))
    for result in ["W", "L"]:
        subset = career_df[career_df["result"] == result]
        ax.scatter(subset["player_age"], subset["age_diff"], s=12, alpha=0.6,
                   color=_COLORS[result], label=_LABELS[result])
    _style_axes(ax, title or "Age gap with opponents over a career")
    return ax