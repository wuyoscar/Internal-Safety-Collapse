# /// script
# dependencies = ["playwright", "pillow"]
# ///
"""Record the project page for the READMEs as two animated WebP files, 1600 px wide.

    uv run assets/readme-figures/record_site.py [SITE_URL]

Writes assets/site-hero.webp (one task in the hero player, from unfinished fields to a passing
check) and assets/site-tools.webp (the "Different tools, different data" stage stepping through
four tools). SITE_URL defaults to http://localhost:8098/ (python -m http.server 8098 in docs/).

The page is captured as screenshots at device scale 2 and each frame is kept for as long as it
was on screen. 1600 px is twice the width a README shows the image at, so text stays sharp on
high-density displays; animated WebP keeps full colour at a fraction of a GIF's size.
"""
import base64
import pathlib
import sys
import tempfile
import time

from PIL import Image
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8098/"
ASSETS = pathlib.Path(__file__).resolve().parent.parent
W, H, OUT_W = 1080, 790, 1600
FIRST = ("aiml_sarcasm", "aiml_sentiment", "aiml_clickbait", "aiml_emotion")  # mild card to record
SEED_JS = """(() => { let a = %d >>> 0; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0;
let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
return ((t ^ t >>> 14) >>> 0) / 4294967296; }; })();"""


def shoot(page, cdp, folder: pathlib.Path, seconds: float, actions=()) -> list:
    """Take screenshots for `seconds`; return [(file, time it stayed on screen)]."""
    folder.mkdir()
    todo, frames, t0 = sorted(actions, key=lambda a: a[0]), [], time.monotonic()
    while (t := time.monotonic() - t0) < seconds:
        while todo and todo[0][0] <= t:
            todo.pop(0)[1]()
        shot = cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 93, "optimizeForSpeed": True})
        file = folder / f"{len(frames):04d}.jpg"
        file.write_bytes(base64.b64decode(shot["data"]))
        frames.append([file, t])
        page.wait_for_timeout(20)
    end = time.monotonic() - t0
    return [(f, (frames[i + 1][1] if i + 1 < len(frames) else end) - t) for i, (f, t) in enumerate(frames)]


def webp(frames: list, dest: pathlib.Path, quality: int) -> None:
    images = [Image.open(f).convert("RGB") for f, _ in frames]
    images = [im.resize((OUT_W, round(im.height * OUT_W / im.width)), Image.Resampling.LANCZOS) for im in images]
    images[0].save(dest, "WEBP", save_all=True, append_images=images[1:], loop=0, quality=quality, method=4,
                   minimize_size=True, duration=[max(20, round(d * 1000)) for _, d in frames])
    print(dest.name, f"{dest.stat().st_size / 1e6:.1f} MB", len(frames), "frames", images[0].size)


with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
    tmp = pathlib.Path(tmp)
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = None
    for seed in range(1, 40):  # the hero shuffles its cards; pick a seed whose second card is mild
        context = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2)
        context.add_init_script(SEED_JS % seed)
        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_selector("#hero-player .hp-frame", timeout=15000)
        # Skip the page-load entrance: wait for the first card to finish, then start with the second one.
        for state in ("3", "0"):
            page.wait_for_function(f"document.querySelector('#hero-player .hp-frame').dataset.s === '{state}'", timeout=20000)
        if page.inner_text("#hero-player .win-url").split(" / ")[0].strip() in FIRST:
            break
        context.close()
        page = None
    if page is None:
        sys.exit("no seed gave a suitable card")
    cdp = page.context.new_cdp_session(page)
    hero = shoot(page, cdp, tmp / "hero", 4.7)  # one card, from ??? to PASS; the loop restarts on the same card
    # The card fades in for the first ~0.45 s. Move those frames to the end so the file opens on the
    # complete card with its ??? fields, and the fade reads as the swap before the loop restarts.
    elapsed, cut = 0.0, 0
    while elapsed < 0.45:
        elapsed += hero[cut][1]
        cut += 1
    hero = hero[cut:] + hero[:cut]

    top = "(s => document.querySelector(s).getBoundingClientRect().top + scrollY - 118)"
    page.evaluate(f"window.scrollTo({{top: {top}('#generality h2'), behavior: 'instant'}})")
    page.wait_for_timeout(900)
    tool = lambda i: lambda: page.evaluate("i => document.querySelectorAll('#gen .gen-tool')[i].click()", i)
    tool(0)()
    page.wait_for_timeout(120)
    tools = shoot(page, cdp, tmp / "tools", 10.4, actions=[(2.6, tool(1)), (5.2, tool(2)), (7.8, tool(4))])
    browser.close()
    webp(hero, ASSETS / "site-hero.webp", 64)
    webp(tools, ASSETS / "site-tools.webp", 70)
