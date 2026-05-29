#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate the static ISC Arena badge (assets/leaderboard_progress.svg).

Self-contained: reads arena_cache.json + isc_cases.json and renders a simple
static card showing the current count of triggered models. No time series, no
history file, no external deps — run it by hand after updating the data.

Usage:
    uv run scripts/gen_leaderboard_chart.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_leaderboard import slug_to_display  # reuse the canonical name mapping

ROOT = Path(__file__).parent.parent
ARENA = ROOT / "assets" / "arena_cache.json"
ISC = ROOT / "assets" / "isc_cases.json"
OUT = ROOT / "assets" / "leaderboard_progress.svg"

BG, CARD, BORDER = "#F8F0F0", "#FFFFFF", "#E0D0D0"
TEXT, TEXT_DIM, RED = "#2D2020", "#6B5555", "#D94040"


def main() -> None:
    arena = json.loads(ARENA.read_text())
    isc = json.loads(ISC.read_text())

    triggered = sum(1 for m in arena if slug_to_display(m["name"]) in isc)

    # Contributor credits: count demos per handle across triggered models.
    counts: Counter[str] = Counter()
    for case in isc.values():
        for d in case.get("demos", []):
            counts[d["by"]] += 1
    top = counts.most_common(5)
    credits = "  ·  ".join(f"@{h} ({n})" for h, n in top)

    w, h = 720, 200
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="'Space Grotesk','Segoe UI',sans-serif">
  <rect width="{w}" height="{h}" rx="14" fill="{BG}"/>
  <text x="{w/2}" y="46" text-anchor="middle" font-size="22" font-weight="700" fill="{RED}" letter-spacing="2">ISC ARENA</text>
  <text x="{w/2}" y="120" text-anchor="middle" font-size="78" font-weight="700" fill="{RED}">{triggered}</text>
  <text x="{w/2}" y="150" text-anchor="middle" font-size="18" font-weight="600" fill="{TEXT}">models triggered under ISC</text>
  <text x="{w/2}" y="180" text-anchor="middle" font-size="13" fill="{TEXT_DIM}">{credits}</text>
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT.name}: {triggered} triggered models | credits: {credits}")


if __name__ == "__main__":
    main()
