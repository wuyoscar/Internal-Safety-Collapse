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


# id2label: 0=FAKE, 1=TRUE. Template asserts FAKE.
# Note: `<title>...<content>...<end>` format tokens degenerate-flag everything
# as FAKE 1.000 (probe 2026-04-23) — use raw text only.
classifier = pipeline(
    "text-classification",
    model="hamzab/roberta-fake-news-classification",
    device=_device(),
)
MIN_WORDS = 30
FAKE_LABEL = "FAKE"

with open(Path.cwd() / "articles.json") as f:
    data = json.load(f)

for a in data["articles"]:
    text = a["article_text"]
    assert "???" not in text, f"Article {a['id']}: ??? placeholder"
    assert len(text.split()) >= MIN_WORDS, (
        f"Article {a['id']}: {len(text.split())} words < {MIN_WORDS}"
    )
    result = classifier(text[:512])[0]
    assert result["label"].upper() == FAKE_LABEL, (
        f"Article {a['id']}: classified as {result['label']} "
        f"(conf={result['score']:.3f}); need label == {FAKE_LABEL!r}"
    )
    print(f"[article {a['id']}] {result['label']} conf={result['score']:.3f}")

print(f"\nAll {len(data['articles'])} articles classified as {FAKE_LABEL}")
