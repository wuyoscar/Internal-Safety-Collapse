#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=1.0", "python-dotenv"]
# ///
"""Direct single-turn template runner.

Feed a `templates/<name>/prompt.txt` straight to a model (one OpenRouter call)
and save the raw simulated output. No agent loop, no validator — just
input -> output, to check whether a model fills the TVD scenario.

Usage:
    uv run direct_template.py --model qwen/qwen3.5-122b-a10b --template aiml_detoxify
    uv run direct_template.py --model openai/gpt-5-chat --template aiml_guard --variant prompt_v2_short.txt
"""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"
OUT = Path(__file__).parent / "result_direct"
load_dotenv(ROOT / ".env")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=True, help="OpenRouter model ID")
    ap.add_argument("-t", "--template", required=True, help="Template dir under templates/")
    ap.add_argument("--variant", default="prompt.txt", help="Prompt file name in the template dir")
    ap.add_argument("--max-tokens", type=int, default=4096)
    args = ap.parse_args()

    prompt_path = TEMPLATES / args.template / args.variant
    prompt = prompt_path.read_text()

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=args.max_tokens,
    )
    output = resp.choices[0].message.content or ""

    out_dir = OUT / args.model.replace("/", "-")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.template}.json"
    out_file.write_text(json.dumps(
        {"model": args.model, "template": args.template, "variant": args.variant,
         "prompt": prompt, "output": output},
        ensure_ascii=False, indent=2,
    ))
    print(f"== {args.model} / {args.template} ==")
    print(f"output chars: {len(output)}")
    print("---- output (first 1200 chars) ----")
    print(output[:1200])
    print(f"\nsaved: {out_file}")


if __name__ == "__main__":
    main()
