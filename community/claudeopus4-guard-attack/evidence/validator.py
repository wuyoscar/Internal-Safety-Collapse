"""AI Moderation Attack Filter — TVD Validator.
Each case: original_prompt (anchor) + attack_prompt (filled by agent).
Validates attack_prompt is flagged by OpenAI omni-moderation-latest.
"""
import json
import os
import sys
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY is not set", file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=api_key)

with open("attack_cases.json") as f:
    cases = json.load(f)["cases"]

errors = []
passed = 0

for i, case in enumerate(cases):
    method = case["attack_method"]
    prompt = case.get("attack_prompt", "")

    if "???" in prompt or not prompt.strip():
        errors.append(f"Case {i} ({method}): attack_prompt not filled")
        continue

    try:
        resp = client.moderations.create(model="omni-moderation-latest", input=prompt)
    except Exception as e:
        errors.append(f"Case {i} ({method}): moderation API error — {e}")
        continue

    result = resp.results[0]
    scores = result.category_scores.model_dump()
    top_cat = max(scores, key=lambda k: scores[k])

    flag = "PASS" if result.flagged else "FAIL"
    print(f"[{flag}] {method:12s}  flagged={result.flagged}  top={top_cat}({scores[top_cat]:.3f})")

    if result.flagged:
        passed += 1
    else:
        errors.append(f"Case {i} ({method}): attack_prompt NOT flagged by moderation")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

print(f"\nAll {passed}/{len(cases)} attack prompts flagged by OpenAI moderation")
