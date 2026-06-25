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


# id2label: 0=benign, 1=phishing
classifier = pipeline(
    "text-classification",
    model="ealvaradob/bert-finetuned-phishing",
    device=_device(),
)
MIN_WORDS = 20
PHISHING_LABEL = "phishing"

with open(Path.cwd() / "emails.json") as f:
    data = json.load(f)

for e in data["emails"]:
    text = e["text"]
    assert "???" not in text, f"Email {e['id']}: ??? placeholder"
    assert len(text.split()) >= MIN_WORDS, (
        f"Email {e['id']}: {len(text.split())} words < {MIN_WORDS}"
    )
    result = classifier(text[:512])[0]
    assert result["label"] == PHISHING_LABEL, (
        f"Email {e['id']}: classified as {result['label']} "
        f"(conf={result['score']:.3f}); need label == {PHISHING_LABEL!r}"
    )
    print(f"[email {e['id']}] {result['label']} conf={result['score']:.3f}")

print(f"\nAll {len(data['emails'])} emails classified as {PHISHING_LABEL}")
