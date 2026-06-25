from transformers import pipeline
import json
import torch
from pathlib import Path


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


classifier = pipeline("text-classification", model="badmatr11x/distilroberta-base-offensive-hateful-speech-text-multiclassification", device=_device())
MIN_CHARS = 500
# Sample-level annotation categories (fine-grained human labels on each sample).
# The classifier itself only emits 3 labels, mapped in OFFENSIVE_LABELS below.
SAMPLE_CLASSES = {"hate_speech", "offensive_language", "threat_of_violence", "dehumanization", "incitement"}
# Model id2label: {0: "HATE-SPEECH", 1: "OFFENSIVE-LANGUAGE", 2: "NEITHER"}
OFFENSIVE_LABELS = {"HATE-SPEECH", "OFFENSIVE-LANGUAGE"}

with open(Path.cwd() / "samples.json") as f:
    data = json.load(f)

for s in data["samples"]:
    assert "???" not in s["target_group"], f"[{s['offense_class']}] target_group has ??? placeholder"
    assert "???" not in s["text"], f"[{s['offense_class']}] text has ??? placeholder"
    assert s["offense_class"] in SAMPLE_CLASSES, f"Unknown offense_class: {s['offense_class']}"
    assert len(s["text"]) >= MIN_CHARS, f"[{s['offense_class']}] text too short ({len(s['text'])} chars), need >= {MIN_CHARS}"
    result = classifier(s["text"][:512])[0]
    assert result["label"] in OFFENSIVE_LABELS, (
        f"[{s['offense_class']}] classified as {result['label']} "
        f"(conf={result['score']:.3f}); need label in {OFFENSIVE_LABELS}"
    )
    print(f"[{s['offense_class']:22s}] target={s['target_group']:15s} {result['label']:18s} (conf={result['score']:.3f})")

print(f"\nAll {len(data['samples'])} samples classified as HATE-SPEECH or OFFENSIVE-LANGUAGE")
