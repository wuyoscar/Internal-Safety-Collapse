#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8"]
# ///
"""Generate the static Frontier LLMs badge (assets/leaderboard_progress.png).

Reads arena_cache.json + isc_cases.json and renders a plain static PNG card
showing the current count of triggered models. PNG (not SVG) so it renders and
opens cleanly on GitHub — no scripts, no time series, no history file.

Usage:
    uv run scripts/gen_leaderboard_chart.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from gen_leaderboard import slug_to_display  # reuse the canonical name mapping

ROOT = Path(__file__).parent.parent
ARENA = ROOT / "assets" / "arena_cache.json"
ISC = ROOT / "assets" / "isc_cases.json"
OUT = ROOT / "assets" / "leaderboard_progress.png"

BG, TEXT, TEXT_DIM, RED = "#F8F0F0", "#2D2020", "#6B5555", "#D94040"


def main() -> None:
    arena = json.loads(ARENA.read_text())
    isc = json.loads(ISC.read_text())
    triggered = sum(1 for m in arena if slug_to_display(m["name"]) in isc)

    counts: Counter[str] = Counter()
    for case in isc.values():
        for d in case.get("demos", []):
            counts[d["by"]] += 1
    credits = "    ·    ".join(f"@{h} ({n})" for h, n in counts.most_common(5))

    fig = plt.figure(figsize=(7.2, 2.0), dpi=200)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.text(0.5, 0.86, "FRONTIER LLMS", ha="center", va="center", color=RED,
            fontsize=15, fontweight="bold", family="sans-serif")
    ax.text(0.5, 0.50, str(triggered), ha="center", va="center", color=RED,
            fontsize=52, fontweight="bold", family="sans-serif")
    ax.text(0.5, 0.20, "models triggered under ISC", ha="center", va="center",
            color=TEXT, fontsize=12, fontweight="bold", family="sans-serif")
    ax.text(0.5, 0.06, credits, ha="center", va="center", color=TEXT_DIM,
            fontsize=8.5, family="sans-serif")
    fig.savefig(OUT, facecolor=BG, bbox_inches="tight", pad_inches=0.25)
    print(f"Wrote {OUT.name}: {triggered} triggered models | credits: {credits}")


if __name__ == "__main__":
    main()
