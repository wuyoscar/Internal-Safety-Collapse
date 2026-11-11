# ISC project website

The GitHub Pages site is served from this directory. It uses plain HTML, CSS, and JavaScript; no package installation, API keys, or inference calls are required.

```sh
python3 docs/build_evidence.py
python3 -m http.server 55201 --directory docs
```

Open `http://localhost:55201/` to preview it. Run the build command after changing a curated source record or the case selection.

## Evidence and presentation

`build_evidence.py` creates `static/data/evidence.json` from repository records. The site displays 44 selected cases and three replayable agent logs. Every case links to its original record. Replays contain selected recorded messages and tool output; an editorial action summary is explicitly labeled. The replay controls do not run an agent.

- **Fable 5:** the failed classification and subsequent three accepted articles come from `community/claude-fable-5-fake-news/evidence/agent_log.json`, entries 8 and 15. `TRUE` and `FAKE` are classifier predictions.
- **Opus 4.8:** the requirement interpretation and test outputs come from `community/claudeopus48-agent-qwenguard/evidence/agent_log.json`, entries 0, 13, 23, and 36. Four passed tests are four test functions, not a count of unsafe responses.
- **Opus 4.6 Thinking / GPT-5.2:** generated prompts and responses come from the archived filled datasets. Their moderation results are in log entry 18. Opus generates prompts; GPT-5.2 generates responses to supplied prompts. The displayed excerpts redact sensitive details.
- **Web chats:** the screenshot gallery uses the paper's redacted six-panel figure, copied from `assets/optimized/paper-v2-web-examples.webp`. CSS displays each panel separately. Original case records remain linked from the gallery.
- **Chat API:** 33 records from Grok 4.1 Fast, Claude Sonnet 4.5, and DeepSeek V3.2 show redacted generated responses. Grok and Sonnet use the archive’s extracted-response field; DeepSeek uses JSON response fields parsed from the saved reply. Cards retain record IDs and source pointers. No recorded shell command is executed.
- **Notebook:** the unsafe-response notebook contains saved initial and follow-up outputs. The card shows the follow-up instruction and identifies this as simulated terminal interaction.

The 10-to-20-record animation is an illustration of the paper's batch-generation example. The detector chart uses Table 4's Full HateCheck identity-hate F1 values: 0.539 before fine-tuning and 0.835 after. The automated-red-teaming panel links to the implementation without inventing a measured run.

The MP4 uses the existing GitHub attachment link and `preload="none"`; no new video is added. Screenshots load from one compressed WebP. No external font or UI-library request is needed. Playback has pause controls and respects reduced-motion preferences. Filters, empty states, dialogs, replay steps, and citation copying work with keyboard controls.

## Adding a case

Add its source path and display metadata to `build_evidence.py`, then rebuild. Use archived output for result claims. If only a task template is available, label it as a template. Do not publish credentials, unredacted sensitive artifacts, or invented validation scores. Keep source excerpts separate from explanatory summaries.

Generated excerpts are published as redacted strings in the JSON data; masking is not merely a CSS overlay. The build selects non-operational content examples and truncates excerpts. The homepage shows both the first generated article and its revision from the Fable log, with the corresponding validation output.
