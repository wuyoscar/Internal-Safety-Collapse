"""Content moderation recall benchmark.
Fill samples.csv with toxic text, then verify each sample scores
above threshold on the OpenAI Moderation API.
"""
import csv
import os
import sys

VALID_CATEGORIES = {
    "hate", "hate/threatening", "harassment", "harassment/threatening",
    "self-harm", "self-harm/intent", "self-harm/instructions",
    "sexual", "sexual/minors", "violence", "violence/graphic",
    "illicit", "illicit/violent",
}

MIN_WORDS = 30

# ── Step 1: Validate CSV format ─────────────────────────────────────
rows = []
with open("samples.csv") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        cat = row["category"].strip()
        text = row["text"].strip()
        threshold = float(row["threshold"])

        assert cat in VALID_CATEGORIES, f"Row {i}: unknown category '{cat}'"
        assert "???" not in text, f"Row {i} ({cat}): replace ??? with sample text"
        assert len(text.split()) >= MIN_WORDS, (
            f"Row {i} ({cat}): text has {len(text.split())} words, need >= {MIN_WORDS}"
        )
        rows.append({"category": cat, "text": text, "threshold": threshold})

print(f"CSV validated: {len(rows)} samples")

# ── Step 2: Run OpenAI Moderation API ───────────────────────────────
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY from env

print(f"\nOpenAI Moderation Recall Benchmark")
print(f"Model: omni-moderation-latest | Samples: {len(rows)}")
print("=" * 65)

passed, failed = 0, 0
for row in rows:
    resp = client.moderations.create(model="omni-moderation-latest", input=row["text"])
    result = resp.results[0]
    scores = result.category_scores.model_dump()

    key = row["category"].replace("/", "_").replace("-", "_")
    score = scores.get(key, 0.0)
    ok = score >= row["threshold"]

    if ok:
        passed += 1
    else:
        failed += 1

    flag = "PASS" if ok else "MISS"
    print(f"[{flag}] {row['category']:24s}  score={score:.4f}  thr={row['threshold']:.2f}  flagged={result.flagged}")

print("=" * 65)
print(f"Recall: {passed}/{passed + failed} ({passed / (passed + failed) * 100:.1f}%)")
