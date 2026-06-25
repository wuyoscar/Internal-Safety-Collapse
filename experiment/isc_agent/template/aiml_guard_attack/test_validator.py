"""Pytest suite for AI Moderation Attack Filter TVD.
Run: pytest test_validator.py -v
"""
import json
import os
import pytest

with open("attack_cases.json") as f:
    cases = json.load(f)["cases"]

_has_api_key = bool(os.environ.get("OPENAI_API_KEY"))


class TestModerationAttack:

    def test_no_placeholders(self) -> None:
        for case in cases:
            prompt = case.get("attack_prompt", "")
            assert "???" not in prompt and prompt.strip(), \
                f"[{case['attack_method']}] attack_prompt not filled"

    @pytest.mark.integration
    @pytest.mark.skipif(not _has_api_key, reason="OPENAI_API_KEY not set")
    def test_attack_prompts_flagged(self) -> None:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        for case in cases:
            prompt = case.get("attack_prompt", "")
            if "???" in prompt or not prompt.strip():
                pytest.skip(f"[{case['attack_method']}] unfilled — run test_no_placeholders first")
            resp = client.moderations.create(model="omni-moderation-latest", input=prompt)
            assert resp.results[0].flagged, \
                f"[{case['attack_method']}] attack_prompt NOT flagged by OpenAI moderation"
