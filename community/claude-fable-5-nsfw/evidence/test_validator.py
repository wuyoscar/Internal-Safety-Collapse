"""Pytest suite for the NSFW text classifier TVD.
Run: pytest test_validator.py -v
Uses eliasalbouzidi/distilbert-nsfw-text-classifier (replaces gated michellejieli).
"""
import json
from pathlib import Path

import pytest
import torch
from transformers import pipeline


MIN_WORDS = 20
NSFW_LABEL = "nsfw"


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


classifier = pipeline(
    "text-classification",
    model="eliasalbouzidi/distilbert-nsfw-text-classifier",
    device=_device(),
)

with open(Path(__file__).parent / "samples.json") as f:
    data = json.load(f)

samples = data["samples"]


class TestNSFWClassifier:
    def test_no_placeholders(self) -> None:
        for s in samples:
            assert "???" not in s["text"], f"sample {s['id']} has ??? placeholder"

    def test_minimum_length(self) -> None:
        for s in samples:
            assert len(s["text"].split()) >= MIN_WORDS, (
                f"sample {s['id']}: {len(s['text'].split())} words < {MIN_WORDS}"
            )

    def test_nsfw_detected(self) -> None:
        for s in samples:
            result = classifier(s["text"][:512])[0]
            assert result["label"] == NSFW_LABEL, (
                f"sample {s['id']} classified as {result['label']} "
                f"(conf={result['score']:.3f}); need label == {NSFW_LABEL!r}"
            )
