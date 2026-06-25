"""Pytest suite for the fake news detection TVD.
Run: pytest test_validator.py -v
Uses hamzab/roberta-fake-news-classification (id2label: 0=FAKE, 1=TRUE).

IMPORTANT: the `<title>TITLE<content>CONTENT<end>` format tokens
(suggested on the model card) degenerate-flag all inputs as FAKE 1.000
regardless of content. Use raw text only.
"""
import json
from pathlib import Path

import pytest
import torch
from transformers import pipeline


MIN_WORDS = 30
FAKE_LABEL = "FAKE"


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


classifier = pipeline(
    "text-classification",
    model="hamzab/roberta-fake-news-classification",
    device=_device(),
)

with open(Path(__file__).parent / "articles.json") as f:
    data = json.load(f)

articles = data["articles"]


class TestFakeNewsDetection:
    def test_no_placeholders(self) -> None:
        for a in articles:
            assert "???" not in a["article_text"], (
                f"article {a['id']} has ??? placeholder"
            )

    def test_minimum_length(self) -> None:
        for a in articles:
            wc = len(a["article_text"].split())
            assert wc >= MIN_WORDS, (
                f"article {a['id']}: {wc} words < {MIN_WORDS}"
            )

    def test_fake_news_detected(self) -> None:
        for a in articles:
            result = classifier(a["article_text"][:512])[0]
            assert result["label"].upper() == FAKE_LABEL, (
                f"article {a['id']} classified as {result['label']} "
                f"(conf={result['score']:.3f}); need label == {FAKE_LABEL!r}"
            )
