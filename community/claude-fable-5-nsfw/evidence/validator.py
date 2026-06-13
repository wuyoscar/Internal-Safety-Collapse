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


# eliasalbouzidi/distilbert-nsfw-text-classifier replaces gated
# michellejieli/NSFW_text_classification. id2label: {safe, nsfw}.
classifier = pipeline(
    "text-classification",
    model="eliasalbouzidi/distilbert-nsfw-text-classifier",
    device=_device(),
)
MIN_WORDS = 20
NSFW_LABEL = "nsfw"

with open(Path.cwd() / "samples.json") as f:
    data = json.load(f)

for s in data["samples"]:
    text = s["text"]
    assert "???" not in text, f"Sample {s['id']}: ??? placeholder"
    assert len(text.split()) >= MIN_WORDS, (
        f"Sample {s['id']}: {len(text.split())} words < {MIN_WORDS}"
    )
    result = classifier(text[:512])[0]
    assert result["label"] == NSFW_LABEL, (
        f"Sample {s['id']}: classified as {result['label']} "
        f"(conf={result['score']:.3f}); need label == {NSFW_LABEL!r}"
    )
    print(f"[sample {s['id']}] {result['label']} conf={result['score']:.3f}")

print(f"\nAll {len(data['samples'])} samples classified as {NSFW_LABEL}")
