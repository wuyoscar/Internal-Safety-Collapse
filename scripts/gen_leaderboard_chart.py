#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8"]
# ///
"""
Generate ISC Arena progress chart.
Reads assets/leaderboard_history.json → assets/leaderboard_progress.svg
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
DATA = ROOT / "assets" / "leaderboard_history.json"
OUT = ROOT / "assets" / "leaderboard_progress.svg"


def main() -> None:
    # -- Premium font stack --
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["SF Pro Display", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.dpi": 200,
    })

    history = json.loads(DATA.read_text())
    dates = [datetime.strptime(h["date"], "%Y-%m-%d") for h in history]
    confirmed = [h["confirmed"] for h in history]
    total = [h["total"] for h in history]

    # Contributors
    contributors: dict[str, int] = {}
    for h in history:
        for ev in h.get("events", []):
            contributors[ev["by"]] = contributors.get(ev["by"], 0) + 1

    latest = history[-1]

    # -- Colors (soft light theme, tech feel) --
    BG = "#F8F0F0"
    CARD = "#FFFFFF"
    BORDER = "#E0D0D0"
    TEXT = "#2D2020"
    TEXT_DIM = "#6B5555"
    RED = "#D94040"
    RED_LIGHT = "#F2DADA"
    GREEN = "#3FB950"

    fig, ax = plt.subplots(figsize=(10, 3.8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # -- Soft fill --
    ax.fill_between(dates, 0, confirmed, color=RED_LIGHT, alpha=0.8, zorder=2)
    ax.fill_between(dates, 0, confirmed, color=RED, alpha=0.08, zorder=2)

    # -- Main line --
    ax.plot(dates, confirmed, color=RED, linewidth=3, zorder=4)

    # -- Data points --
    for i, (d, c) in enumerate(zip(dates, confirmed)):
        if c > 0:
            ax.plot(d, c, "o", color=RED, markersize=8, markerfacecolor="white",
                    markeredgecolor=RED, markeredgewidth=2.5, zorder=6)
            # Only annotate points where value changes significantly to avoid crowding
            prev = confirmed[i - 1] if i > 0 else 0
            if c != prev:
                ax.annotate(str(c), xy=(d, c), xytext=(0, 13),
                            textcoords="offset points", fontsize=13,
                            fontweight="bold", color=RED, ha="center", zorder=7)

    # -- Stats badge (top-right) -- numerator only (count of triggered models)
    badge_text = f"  {latest['confirmed']} triggered  "
    ax.text(0.97, 0.88, badge_text, transform=ax.transAxes,
            fontsize=14, fontweight="bold", color=TEXT,
            ha="right", va="top", family="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=CARD,
                      edgecolor=BORDER, linewidth=1))

    # -- Title (centered, RED) --
    ax.text(0.5, 0.92, "ISC ARENA", transform=ax.transAxes,
            fontsize=18, fontweight="bold", color=RED,
            ha="center", va="top")

    # -- Contributors (bottom, centered) --
    contrib_parts = [f"@{k} ({v})" for k, v in sorted(contributors.items(), key=lambda x: -x[1])]
    ax.text(0.5, -0.20, "  ·  ".join(contrib_parts),
            transform=ax.transAxes, fontsize=12, color=TEXT_DIM,
            ha="center", fontweight="bold")

    # -- Axes styling --
    y_max = max(confirmed) * 1.8 + 3
    ax.set_ylim(0, y_max)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=5))

    # X-axis — auto-space ticks so labels don't overlap
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    pad = (dates[-1] - dates[0]) * 0.08 if len(dates) > 1 else timedelta(days=3)
    ax.set_xlim(dates[0] - pad, dates[-1] + pad)

    # Tick styling
    ax.tick_params(axis="both", colors=TEXT, labelsize=11, length=0)
    ax.tick_params(axis="x", pad=8, rotation=0)
    ax.tick_params(axis="y", pad=6)

    # Grid
    ax.grid(axis="y", color=BORDER, linewidth=0.6, alpha=0.6)
    ax.grid(axis="x", visible=False)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Bottom line only
    ax.axhline(y=0, color=BORDER, linewidth=1)

    fig.tight_layout(pad=1.5)
    fig.savefig(OUT, format="svg", bbox_inches="tight", facecolor=BG)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
