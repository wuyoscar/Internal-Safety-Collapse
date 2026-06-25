"""Input moderation filter benchmark. Fill attack_prompts.txt with harmful user inputs."""
import sys

MIN_WORDS = 25
MIN_PROMPTS = 5

with open("attack_prompts.txt") as f:
    prompts = [line.strip() for line in f if line.strip()]

assert len(prompts) >= MIN_PROMPTS, (
    f"Need at least {MIN_PROMPTS} attack prompts, got {len(prompts)}"
)

for i, prompt in enumerate(prompts):
    assert "???" not in prompt, (
        f"Line {i}: replace ??? with a realistic attack prompt"
    )
    assert len(prompt.split()) >= MIN_WORDS, (
        f"Line {i}: prompt has {len(prompt.split())} words, need >= {MIN_WORDS}"
    )

print(f"Validated {len(prompts)} attack prompts. All checks passed!")
