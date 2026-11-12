# /// script
# dependencies = ["playwright", "pillow"]
# ///
"""Render the README figures in this folder to PNG and lossless WebP.

Run from the repository root:  uv run assets/readme-figures/render.py
Uses the installed Google Chrome; fonts load from Google Fonts.
"""
import pathlib

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent
FIGURES = {
    "agent-run": "readme-agent-run",
    "template-variants": "readme-template-variants",
    "workspace-trajectory": "readme-workspace-trajectory",
    "score-steering": "readme-score-steering",
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1100, "height": 600}, device_scale_factor=2)
    for source, name in FIGURES.items():
        page.goto((HERE / f"{source}.html").as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        png = ASSETS / f"{name}.png"
        page.screenshot(path=str(png), full_page=True)
        Image.open(png).save(ASSETS / "optimized" / f"{name}.webp", lossless=True, method=6)
        print(png.name, Image.open(png).size)
    browser.close()
