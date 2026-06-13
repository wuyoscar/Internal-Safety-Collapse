#!/bin/bash
# Verify an ISC-Bench template:
#   1. Run each prompt variant against a model
#   2. Save outputs to the template folder (lowercased names)
#   3. Convert README.md → SKILL.md (merge meta.json into it)
#   4. Delete meta.json
#
# Usage:
#   ./scripts/verify_template.sh codebase_templates/aiml_moderation
#   ./scripts/verify_template.sh codebase_templates/aiml_moderation --model google/gemini-2.5-pro

set -e

TEMPLATE_DIR="$1"
MODEL="${2:---model}"
MODEL_ID="${3:-qwen/qwen3-coder}"

if [ "$MODEL" = "--model" ] && [ -n "$3" ]; then
    MODEL_ID="$3"
fi

if [ -z "$TEMPLATE_DIR" ] || [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Usage: $0 <template-dir> [--model <model-id>]"
    exit 1
fi

echo "=== Verifying: $TEMPLATE_DIR ==="
echo "Model: $MODEL_ID"
echo ""

# Find all prompt files
PROMPTS=$(ls "$TEMPLATE_DIR"/prompt*.txt 2>/dev/null)
if [ -z "$PROMPTS" ]; then
    echo "ERROR: No prompt*.txt files found in $TEMPLATE_DIR"
    exit 1
fi

# Run each prompt and save output
for PROMPT_FILE in $PROMPTS; do
    BASENAME=$(basename "$PROMPT_FILE" .txt)
    OUTPUT_FILE="$TEMPLATE_DIR/output_${BASENAME#prompt_}.txt"

    # If it's just "prompt.txt", output is "output.txt"
    if [ "$BASENAME" = "prompt" ]; then
        OUTPUT_FILE="$TEMPLATE_DIR/output.txt"
    fi

    echo "--- Running: $BASENAME ---"
    cat "$PROMPT_FILE" | uv run --with "openai>=1.0" python3 -c "
import os, sys
from openai import OpenAI
client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.environ['OPENROUTER_API_KEY'])
prompt = sys.stdin.read()
resp = client.chat.completions.create(model='$MODEL_ID', messages=[{'role':'user','content':prompt}], max_tokens=4096, temperature=0.0)
print(resp.choices[0].message.content)
" > "$OUTPUT_FILE" 2>/dev/null

    WORDS=$(wc -w < "$OUTPUT_FILE")
    echo "  Output: $OUTPUT_FILE ($WORDS words)"
done

echo ""
echo "=== Done. Outputs saved to $TEMPLATE_DIR ==="
