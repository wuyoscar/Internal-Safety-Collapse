# ISC project website

GitHub Pages serves this directory. The site uses plain HTML, CSS, and JavaScript, with no inference calls, API keys, or frontend build dependencies.

```sh
python3 docs/build_evidence.py
python3 -m http.server 55201 --directory docs
```

Open `http://localhost:55201/`. Run the builder after changing case selection, source records, CSS, or JavaScript. It also updates content-based version parameters for both stylesheets, the script, and evidence data. This prevents browsers from combining the new page with cached assets from an older release; unchanged files keep the same URL.

## One workspace, different data

The video introduces the project at the top of the page. A large editor window follows, with task and file selection on the left, code above a terminal in the middle, and agent activity on the right. The maximize button expands the window; Escape restores it. At narrow widths, code and terminal remain visible together, with the current agent message below them. Only the optional task/file picker opens as a drawer; playback never requires switching panels. The default code view follows three agent workflows:

- **News articles / Fable 5:** nine stages, covering workspace inspection, unfinished data, the first failed check, classifier probes, dataset revision, and final validation. The source is `community/claude-fable-5-fake-news/evidence/agent_log.json`, entries 1–15. `TRUE` and `FAKE` are classifier predictions, not independent fact checks.
- **Toxicity dataset / GPT-5.1:** ten stages based on `community/gpt51-guard-attack-v2/evidence/detoxify/agent_log.json`, entries 1–20. Direct classifier probes are distinguished from saved data and final tests. The identity-attack score changes from 0.07045069 to 0.029264858 and then 0.8275614; the target threshold is 0.5. Four passed tests cover three records.
- **Paired responses / Opus 4.8:** thirteen stages based on `community/claudeopus48-agent-qwenguard/evidence/agent_log.json`, entries 1–36. The runtime file is `test_cases.json`; the public completed artifact is archived as `test_case.json`. Four passed tests are four test functions.

`build_agent_activity.py` attaches the shell calls, outputs, and assistant messages from those logs. It includes file inspection, Python data writes, validator calls, and the paired-response workflow’s timeouts, background pytest run, and polling. Commands retain their source indices. The terminal also retains real weight-loading progress, download messages, device information, and warnings. Long logs keep their measured results and indicate any skipped lines. No loading percentages or runtime results are invented. Timeouts leave the final-test check pending. The code view shows line numbers, syntax colors, red unsafe fields, and green safe fields; the adjacent terminal retains earlier steps as playback advances.

`build_chat_trajectories.py` separately reads three saved chat replies for LlamaGuard, sentiment, and news classification. The **Chat** selector shows commands and outputs present in those replies. Expected results remain chat messages; these trajectories never acquire real execution or test-pass states.

The **Tasks** selector adds ten presentation walkthroughs for chemistry/CIF, biology/FASTA, cybersecurity/NIDS, sarcasm, propaganda, PII/NER, clickbait, emotion, CoNLL-U, and VADER. `build_workspace_walkthroughs.py` combines current task code with 22 curated excerpts from local `output.txt` files. The old outputs use several earlier schemas, so the walkthroughs explicitly adapt them to current fields. Connecting shell steps are presentation instructions; no classifier scores, model-loading output, or passing checks are invented. The propaganda walkthrough uses editorial neutral comparison text alongside the archived propaganda excerpt. An example’s **▶ Task** button opens its corresponding walkthrough.

The three interdisciplinary walkthroughs review output formats: CIF structure records with pymatgen, FASTA records with pyfaidx, and intrusion-detection profiles. Their six excerpts retain the source structure while fully masking scientific identities, coordinates, sequence bases, targets, and operational traffic/evasion descriptions. Record numbers and redaction-block lengths are display conventions. These are artifact-inspection presentations, with no scientific validation outcome inferred from them.

`build_workflows.py` reads recorded Python assignments with `ast.literal_eval`. It never executes the recorded programs. Candidate buffers are labeled as in-memory classifier inputs, and saved data is shown only after the corresponding write. Explanatory action summaries are marked separately from recorded messages and tool outputs.

`workspace-motion.js` coordinates finite file-tab, editor, terminal, and phase transitions. Write steps show changed-line highlights and a typing cursor. Pause/resume also freezes and continues the typing animation. The motion layer observes reduced-motion settings and document visibility and cancels prior transitions before starting another.

Playback starts when the workspace becomes visible, reveals changes progressively, and can cycle through tasks. Pause, step buttons, a timeline, a position slider, and speed selection support manual inspection. Reduced-motion settings disable automatic playback and typing effects; hidden tabs pause playback.

## Example selection

**Examples** keeps 96 cases in the same editor and feedback panes. LlamaGuard, Toxic-BERT, and PyOD appear first, followed by news classification, Detoxify, Qwen3Guard, sentiment, moderation, and web-chat screenshots. The picker searches example titles, task text, tool names, and LLM names. Readers can select with the mouse or arrow keys and Enter, use the previous/next buttons, or play through a task's examples. Opening the picker pauses playback; Escape restores the current choice.

The **Text** view presents articles in a serif face, responses in a sans-serif face, and paired safe/unsafe responses as labeled blocks. **Code / Raw** shows the serialized excerpt in monospace. Terminal output uses monospace while agent messages use prose typography. This mode cycles archived examples without inventing a tool-execution sequence.

`static/data/workspace-outputs.json` retains source-file and context hashes, original relative paths, record pointers, and display changes for the 22 curated local outputs. Raw ignored output files are not uploaded. Name placeholders such as `President [Name]` are masked as `President ███` in displayed excerpts.

Every case retains its source path. The 33 Chat API examples come from saved Grok 4.1 Fast, Claude Sonnet 4.5, and DeepSeek V3.2 records. Grok and Sonnet use the archive's extracted-response field; DeepSeek uses JSON response fields parsed from the saved reply. Source record IDs and pointers remain available.

`static/data/additional-cases.json` adds 12 Toxic-BERT excerpts, 12 PyOD excerpts, four news examples, and one sentiment example. The main-experiment excerpts come from the local `NIPS-ISC-Code-Share` archive and retain relative paths, source hashes, record IDs, and extraction locations. Their public source links point to this curated excerpt file, because the full raw runs are not published here. Toxic-BERT uses `unitary/toxic-bert` with a strict score threshold of `> 0.5`; PyOD requires an outlier as the last sample and normal reference samples. These are single-turn responses, not executed agent trajectories. A further Detoxify dataset is taken from the existing toxicity workflow's final saved data.

Opus 4.6 Thinking generates prompts for named methods; GPT-5.2 generates responses to supplied prompts. Their moderation flags are not presented as a measured jailbreak of an independent target LLM. The notebook entry is explicitly a follow-up instruction with saved outputs available at its source.

Screenshots come from the paper's redacted six-panel figure, copied from `assets/optimized/paper-v2-web-examples.webp`; CSS displays individual panels. Generated excerpts are redacted before publication in JSON, rather than hidden behind a CSS overlay. Sensitive details are masked and excerpts shortened.

## Reported triggers and media

Below the workspace, a compact searchable index mirrors all 62 reported LLM entries and evidence URLs from the English README. This is an archive index, not a ranking or a claim that every setup succeeds. Task-library and experiment links remain available. The previous explanatory application panels are removed so the page concentrates on outputs and reported results.

The feedback pane shows the text being written or checked alongside the recorded result. These excerpts come from the same frame as the editable-data view; blank fields are not presented as generated content. Safe/unsafe response pairs retain separate labels.

The MP4 uses the existing GitHub attachment and `preload="none"`. `video-poster.jpg` is a still from the existing repository video. No new MP4 is added. Fonts use local system stacks. The browser loads one compressed screenshot image and curated JSON data. Citation details are collapsed at the bottom.

## Adding evidence

Add public-source cases in `build_evidence.py`, curated source excerpts in `static/data/additional-cases.json`, and chronological workflows in `build_workflows.py`. Attach agent activity in `build_agent_activity.py`, extract chat trajectories in `build_chat_trajectories.py`, or add presentation sequences through `build_workspace_walkthroughs.py`, then rebuild. Check each frame against its source entry. Preserve the distinction between generated data, in-memory probes, complete validation runs, and editorial summaries. Use recorded output for result claims; label task templates as templates. Keep corrective context when shortening responses. Do not include credentials or unredacted operational details.
