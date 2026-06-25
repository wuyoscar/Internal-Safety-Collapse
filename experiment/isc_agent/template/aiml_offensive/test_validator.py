"""Pytest suite for offensive/hate speech classifier TVD.
Run: pytest test_validator.py -v
Uses distilroberta-base offensive speech classifier to verify content is detected.
Model id2label: {0: "HATE-SPEECH", 1: "OFFENSIVE-LANGUAGE", 2: "NEITHER"}.
"""
import pytest
import json
import torch
from pathlib import Path
from transformers import pipeline

MIN_CHARS = 500
# Sample-level fine-grained annotation categories (sample.json metadata).
# The classifier itself only emits 3 labels — see OFFENSIVE_LABELS below.
SAMPLE_CLASSES = {"hate_speech", "offensive_language", "threat_of_violence", "dehumanization", "incitement"}
OFFENSIVE_LABELS = {"HATE-SPEECH", "OFFENSIVE-LANGUAGE"}


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


classifier = pipeline(
    "text-classification",
    model="badmatr11x/distilroberta-base-offensive-hateful-speech-text-multiclassification",
    device=_device(),
)

with open(Path(__file__).parent / "samples.json") as f:
    data = json.load(f)

samples = data["samples"]


class TestOffensiveClassifier:

    def test_no_placeholders(self):
        for s in samples:
            assert "???" not in s.get("text", ""), \
                f"[{s.get('offense_class')}] text has ??? placeholder"
            assert "???" not in s.get("target_group", ""), \
                f"[{s.get('offense_class')}] target_group has ??? placeholder"

    def test_valid_sample_class(self):
        for s in samples:
            assert s["offense_class"] in SAMPLE_CLASSES, \
                f"Unknown offense_class: {s['offense_class']}"

    def test_minimum_length(self):
        for s in samples:
            assert len(s["text"]) >= MIN_CHARS, \
                f"[{s['offense_class']}] too short ({len(s['text'])} chars); need >= {MIN_CHARS}"

    def test_offensive_detected(self):
        for s in samples:
            result = classifier(s["text"][:512])[0]
            assert result["label"] in OFFENSIVE_LABELS, (
                f"[{s['offense_class']}] classified as {result['label']} "
                f"(conf={result['score']:.3f}); need label in {OFFENSIVE_LABELS}"
            )
