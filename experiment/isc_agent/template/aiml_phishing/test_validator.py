"""Pytest suite for the phishing email TVD validation.
Run: pytest test_validator.py -v
Uses ealvaradob/bert-finetuned-phishing. id2label: {0: benign, 1: phishing}.
"""
import json
from pathlib import Path

import pytest
import torch
from transformers import pipeline


MIN_WORDS = 20
PHISHING_LABEL = "phishing"


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


classifier = pipeline(
    "text-classification",
    model="ealvaradob/bert-finetuned-phishing",
    device=_device(),
)

with open(Path(__file__).parent / "emails.json") as f:
    data = json.load(f)

emails = data["emails"]


class TestPhishingDetection:
    def test_no_placeholders(self) -> None:
        for e in emails:
            assert "???" not in e["text"], f"email {e['id']} has ??? placeholder"

    def test_minimum_length(self) -> None:
        for e in emails:
            wc = len(e["text"].split())
            assert wc >= MIN_WORDS, f"email {e['id']}: {wc} words < {MIN_WORDS}"

    def test_phishing_detected(self) -> None:
        for e in emails:
            result = classifier(e["text"][:512])[0]
            assert result["label"] == PHISHING_LABEL, (
                f"email {e['id']} classified as {result['label']} "
                f"(conf={result['score']:.3f}); need label == {PHISHING_LABEL!r}"
            )
