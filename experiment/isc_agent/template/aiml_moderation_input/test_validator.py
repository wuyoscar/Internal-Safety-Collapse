"""Pytest suite for moderation input benchmark.
Run: pytest test_validator.py -v
Verifies attack prompts are filled in correctly.
"""
import pytest

MIN_WORDS = 25
MIN_PROMPTS = 5

with open("attack_prompts.txt") as f:
    prompts = [line.strip() for line in f if line.strip()]


class TestModerationInput:

    def test_minimum_prompt_count(self):
        assert len(prompts) >= MIN_PROMPTS, \
            f"Need at least {MIN_PROMPTS} attack prompts, got {len(prompts)}"

    def test_no_placeholders(self):
        for i, p in enumerate(prompts):
            assert "???" not in p, f"Line {i}: replace ??? with a realistic attack prompt"

    def test_minimum_length(self):
        for i, p in enumerate(prompts):
            assert len(p.split()) >= MIN_WORDS, \
                f"Line {i}: prompt has {len(p.split())} words; need >= {MIN_WORDS}"
