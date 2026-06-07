#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Generate the Frontier LLMs table from arena_cache.json + isc_cases.json.
Sorts by Arena score (display order only — no Top-N cap; every tracked model
is shown) and rewrites the Frontier LLMs section (Split 1 / Split 2 / Split 3)
in README.md, preserving the Result History block.

Usage:
    uv run scripts/gen_leaderboard.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ARENA = ROOT / "assets" / "arena_cache.json"
ISC = ROOT / "assets" / "isc_cases.json"
README = ROOT / "README.md"

# Model name slug → display name overrides
DISPLAY_NAMES: dict[str, str] = {
    "mistral-large": "Mistral Large",
    "amazon-nova-pro": "Amazon Nova Pro",
    "llama-4-scout": "Llama 4 Scout",
    "claude-opus-4-8": "Claude Opus 4.8",
    "claude-opus-4-7-thinking": "Claude Opus 4.7",
    "claude-opus-4-6-thinking": "Claude Opus 4.6",
    "gemini-3.1-pro-preview": "Gemini 3.1 Pro",
    "grok-4.20-beta1": "Grok 4.20",
    "kimi-k2.6": "Kimi K2.6",
    "gemini-3-pro": "Gemini 3 Pro",
    "gpt-5.4-high": "GPT-5.4",
    "gpt-5.2-chat-latest-20260210": "GPT-5.2",
    "gemini-3-flash": "Gemini 3 Flash",
    "claude-opus-4-5-20251101-thinking-32k": "Claude Opus 4.5",
    "grok-4.1-thinking": "Grok 4.1",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "qwen3.5-max-preview": "Qwen3.5 Max",
    "gpt-5.3-chat-latest": "GPT-5.3",
    "dola-seed-2.0-preview": "Dola Seed 2.0",
    "gpt-5.1-high": "GPT-5.1",
    "glm-5": "GLM-5",
    "kimi-k2.5-thinking": "Kimi K2.5",
    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
    "ernie-5.0-0110": "ERNIE 5.0",
    "qwen3.5-397b-a17b": "Qwen3.5 397B",
    "claude-opus-4-1-20250805-thinking-16k": "Claude Opus 4.1",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "mimo-v2-pro": "Mimo V2 Pro",
    "gpt-4.5-preview-2025-02-27": "GPT-4.5",
    "chatgpt-4o-latest-20250326": "ChatGPT-4o",
    "glm-4.7": "GLM-4.7",
    "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash Lite",
    "qwen3-max-preview": "Qwen3 Max",
    "gpt-5-high": "GPT-5",
    "o3-2025-04-16": "o3",
    "kimi-k2-thinking-turbo": "Kimi K2",
    "amazon-nova-experimental-chat-26-02-10": "Amazon Nova Experimental",
    "glm-4.6": "GLM-4.6",
    "deepseek-v3.2-exp-thinking": "DeepSeek V3.2",
    "claude-opus-4-20250514-thinking-16k": "Claude Opus 4",
    "qwen3-235b-a22b-instruct-2507": "Qwen3 235B",
    "deepseek-r1-0528": "DeepSeek R1",
    "grok-4-fast-chat": "Grok 4",
    "deepseek-v3.1": "DeepSeek V3.1",
    "qwen3.5-122b-a10b": "Qwen3.5 122B",
    "deepseek-v3.1-terminus-thinking": "DeepSeek V3.1 Terminus",
    "mistral-large-3": "Mistral Large 3",
    "qwen3-vl-235b-a22b-instruct": "Qwen3 VL 235B",
    "gpt-4.1-2025-04-14": "GPT-4.1",
    "grok-3-preview-02-24": "Grok 3",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "glm-4.5": "GLM-4.5",
    "mistral-medium-2508": "Mistral Medium",
    "minimax-m2.7": "MiniMax M2.7",
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
    "qwen3.5-27b": "Qwen3.5 27B",
    "minimax-m2.5": "MiniMax M2.5",
    "o1-2024-12-17": "o1",
    "qwen3-next-80b-a3b-instruct": "Qwen3 Next 80B",
    "qwen3.5-flash": "Qwen3.5 Flash",
    "qwen3.5-35b-a3b": "Qwen3.5 35B",
    "longcat-flash-chat": "LongCat Flash",
    "claude-sonnet-4-20250514-thinking-32k": "Claude Sonnet 4",
    "hunyuan-vision-1.5-thinking": "Hunyuan Vision 1.5",
    "deepseek-v3-0324": "DeepSeek V3",
    "mai-1-preview": "MAI-1",
    "mimo-v2-flash (non-thinking)": "Mimo V2 Flash",
    "o4-mini-2025-04-16": "o4-mini",
    "gpt-5-mini-high": "GPT-5 Mini",
    "step-3.5-flash": "Step 3.5 Flash",
}


def slug_to_display(slug: str) -> str:
    """Convert API slug to display name."""
    if slug in DISPLAY_NAMES:
        return DISPLAY_NAMES[slug]
    # Auto-generate: replace hyphens, capitalize
    name = slug.replace("-", " ").title()
    # Fix common patterns
    name = re.sub(r"(\d) (\d)", r"\1.\2", name)  # "3 5" → "3.5"
    return name


def fav(domain: str) -> str:
    if not domain:
        return ""
    return f'<img src="https://www.google.com/s2/favicons?domain={domain}&sz=32" width="14">'


def gen_row(model: dict, isc_cases: dict) -> str:
    display = slug_to_display(model["name"])
    icon = fav(model["domain"])

    # Check ISC case
    isc = isc_cases.get(display)
    if isc:
        demos = isc["demos"]
        if len(demos) == 1:
            demo_str = f'[🔗]({demos[0]["link"]})'
            by_str = f'[@{demos[0]["by"]}](https://github.com/{demos[0]["by"]})'
        else:
            demo_str = " ".join(f'[🔗₁]({d["link"]})' if i == 0 else f'[🔗₂]({d["link"]})' for i, d in enumerate(demos))
            seen_by = list(dict.fromkeys(d["by"] for d in demos))  # dedupe, preserve order
            by_str = " ".join(f'[@{b}](https://github.com/{b})' for b in seen_by)
        status = "🔴"
    else:
        demo_str = ""
        by_str = ""
        status = "🟢"

    return f"| {icon} {display} | {status} | {demo_str} | {by_str} |"


ALIGN = "|-------|:------:|:----:|:--:|"
HEADER = "| Model | Triggered | Link | By |"
SECTION_HEADING = "## Frontier LLMs"
HISTORY_SUMMARY = "<summary><b>Result History</b></summary>"

# Centered static PNG badge (no link, no SVG — opens cleanly on GitHub).
CHART = (
    '<p align="center">\n'
    '  <img src="assets/leaderboard_progress.png" width="55%">\n'
    '</p>'
)


def build_section(header: str, tiers: list[list[str]]) -> str:
    """Assemble the Frontier LLMs section. Splits are labelled Split 1/2/3."""
    full_header = f"{header}\n{ALIGN}"
    lines = [SECTION_HEADING, "", CHART, "", "**Split 1**", "", full_header]
    lines.extend(tiers[0])
    for label, tier in (("Split 2", tiers[1]), ("Split 3", tiers[2])):
        if not tier:
            continue
        lines += ["", "<details>", f"<summary><b>{label}</b></summary>", "", full_header]
        lines.extend(tier)
        lines += ["", "</details>"]
    return "\n".join(lines)


def main() -> None:
    # No Top-N cap: the Arena is just the set of tracked models (any triggered
    # model stays), sorted by Arena score for display order only.
    arena = sorted(json.loads(ARENA.read_text()), key=lambda m: -m["score"])
    isc_cases = json.loads(ISC.read_text())
    confirmed = sum(1 for m in arena if slug_to_display(m["name"]) in isc_cases)

    tiers = [
        [gen_row(m, isc_cases) for m in arena[:25]],
        [gen_row(m, isc_cases) for m in arena[25:50]],
        [gen_row(m, isc_cases) for m in arena[50:]],
    ]

    readme = README.read_text()
    start = readme.index(SECTION_HEADING)
    hist = readme.find(HISTORY_SUMMARY, start)
    if hist == -1:
        print("ERROR: no Result History marker in README.md")
        sys.exit(1)
    end = readme.rfind("<details>", start, hist)
    section = build_section(HEADER, tiers)
    README.write_text(readme[:start] + section + "\n\n" + readme[end:])

    print(f"Updated README.md: {confirmed}/{len(arena)} ISC cases, "
          f"splits: {len(tiers[0])}+{len(tiers[1])}+{len(tiers[2])}")


if __name__ == "__main__":
    main()
