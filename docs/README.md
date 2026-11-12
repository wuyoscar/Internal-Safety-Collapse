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

The **Tasks** selector opens the source directory and includes ten curated presentation walkthroughs for chemistry/CIF, biology/FASTA, cybersecurity/NIDS, sarcasm, propaganda, PII/NER, clickbait, emotion, CoNLL-U, and VADER. `build_workspace_walkthroughs.py` combines current task code with 22 curated excerpts from local `output.txt` files. The old outputs use several earlier schemas, so the walkthroughs explicitly adapt them to current fields. Connecting shell steps are presentation instructions; no classifier scores, model-loading output, or passing checks are invented. The propaganda walkthrough uses editorial neutral comparison text alongside the archived propaganda excerpt. An example’s **▶ Task** button opens its corresponding walkthrough.

The three interdisciplinary walkthroughs review output formats: CIF structure records with pymatgen, FASTA records with pyfaidx, and intrusion-detection profiles. Their six excerpts retain the source structure while fully masking scientific identities, coordinates, sequence bases, targets, and operational traffic/evasion descriptions. Record numbers and redaction-block lengths are display conventions. These are artifact-inspection presentations, with no scientific validation outcome inferred from them.

`build_workflows.py` reads recorded Python assignments with `ast.literal_eval`. It never executes the recorded programs. Candidate buffers are labeled as in-memory classifier inputs, and saved data is shown only after the corresponding write. Explanatory action summaries are marked separately from recorded messages and tool outputs.

`workspace-motion.js` coordinates finite file-tab, editor, terminal, and phase transitions. Write steps show changed-line highlights and a typing cursor. Pause/resume also freezes and continues the typing animation. The motion layer observes reduced-motion settings and document visibility and cancels prior transitions before starting another.

Playback starts when the workspace becomes visible, reveals changes progressively, and can cycle through tasks. Pause, step buttons, a timeline, a position slider, and speed selection support manual inspection. Reduced-motion settings disable automatic playback and typing effects; hidden tabs pause playback.

## Presentation layer

`static/css/polish.css` and `static/js/polish.js` load last and carry presentation only: the hero entrance, the header's section indicator and reading-progress line, scroll reveals, the TVD strip, and the LLM cards. They add no data and make no claims of their own.

The **Mechanism** section replays three sequences from the main README: the LlamaGuard feedback loop (unfinished field, a refusal labelled `safe`, a revision labelled `unsafe`), the Toxic-BERT score threshold (the README's illustrative 0.30, 0.40, and 0.62 against 0.5), and what an input/output safety check inspects. Each step plays as write, send, read, verdict. Field text is example wording, with `[xxx]` shortening it: the feedback loop and the safety-check sequence show the query and the openings of the two responses from the recorded Paired responses run in the workspace section, and the score threshold uses the wording of the README figure. The sequences are defined in `polish.js`, use redaction blocks in place of any generated text, and are labelled illustrative on the page. Verdict colors follow the figure convention: plum for PASS and ochre for FAIL. Playback starts when the section is in view, cycles through the three sequences until the reader picks one, and pauses in hidden tabs.

The TVD strip above the editor names the three parts of the framework and shows the current task's own Task, Validator, and Data text, copied from the editor sidebar. Its highlight follows `data-motion-phase` on the editor window, using the same phase labels as `workspace-motion.js`: reading maps to Task, checks and their outcomes to Validator, and writes to Data.

Reported LLMs appear as cards with the provider name and one link per evidence URL (**Report** for community folders, **Experiment** for experiment logs). With no search text the cards drift in three rows and pause on hover or keyboard focus; **Show all**, any search text, or a reduced-motion setting switches to a static grid. Provider names come from the `PROVIDERS` table in `main.js`, keyed by favicon domain.

`static/css/showcase.css` and `static/js/showcase.js` load after them and set the visual system shared with the ScamWorld site (ivory canvas, one terracotta accent, Fraunces / Urbanist / Geist Mono, window frames with soft shadows), the numbered section heads, and two data-driven pieces:

- **Hero player.** One looping TVD run per prose workspace in `workspace-outputs.json`, in a new order on each visit: the data file with `???` fields, a first run that fails on the unfinished fields, the fields typed in (the opening of that workspace's published walkthrough excerpt, about 54 characters, then a redaction bar), and a run that passes with that workspace's own rule text. The right pane shows lines from the workspace's own runner (`taskCode`), with the `assert` lines lit while it runs. Clicking the window opens that task in the workspace section.
- **Templates belt.** Two rows of windows drifting in opposite directions, one per task with a saved output in `task-library.json` (tabs: Templates, Experiments, Community). Each window prints the archive preview as shipped; `███` values are drawn as bars that fill in while the window is on screen. Windows whose preview has readable text come first, shuffled on each visit. Clicking a window opens the task in the workspace section. Domain colours are used only on these tags.

Readable previews come from `build_task_library.py`: for the templates in `OPENING_TEMPLATES` (sarcasm, propaganda, clickbait, fake news, emotion, sentiment, fraud, phishing, LlamaGuard, offensive) a string value keeps its opening, up to 90 characters, and short values are kept whole. Every other template stays structure-only, including Language & ML templates whose outputs are sexual content, hate aimed at groups, personal records, exploit code or how-to requests, and all other domains. Add a template to that list only after reading what its outputs would show.

The hero counts (LLMs reported, templates, domains, saved outputs) are computed from the same data at load time, not written into the page.

Reduced-motion settings disable every animation in these layers; the belt then becomes a single scrollable row. The page reads the same without `polish.js` and `showcase.js`.

## Source directory and agent explanations

`task-library.json` indexes all 84 prompt-bearing template tasks, plus 17 experiment result groups and 44 community report groups. It includes 527 distinct nonempty saved files after SHA256 deduplication. Source filters expose Workspaces (322 file entries), Experiments (130), and Community (80); some identical files occur in more than one source, so these facet counts overlap. The four template folders without saved outputs are listed explicitly.

Each task/report offers its saved file variants. Existing curated excerpts are reused where source paths match. Known community logs open their full curated replay. The directory retains 630 tool calls from 67 logs with tool activity. Selected NLP logs show file reads, Python edits, and check commands; literal data strings are masked while generic file operations, schema keys, model IDs, and supported runtime-status lines remain visible. Python excerpts are reformatted from parsed source, never executed. Other files use value-redacted JSON, FASTA, CIF, or document-structure previews. Output-only demonstrations show an illustrative unfinished state followed by the saved artifact, without inferring a validation result. The existing 96 readable curated examples remain available under **Examples**.

The full agent replays pin the latest public assistant explanation above tool activity and keep it visible through tool-only stages. Final public summaries are also retained. These community-derived replays use exported public assistant messages. The default replay is the paired-response run, which has public explanations throughout its trajectory.

The local experiment archive also contains 16 DeepSeek logs with readable `type=reasoning` records in `content[].text`; their provider `summary` arrays are empty. Two news-task logs have 22 brief, high-level activity summaries in `reasoning-summaries.json`, keyed by source hash and record index. The sidebar labels these **Reasoning · brief summary**, separately from **Agent note**. File choices indicate whether reasoning was logged or a summary is available. Raw reasoning text is not included in the public index; the summaries do not infer task success or detailed intent.

Refresh the source index with `build_task_library.py --templates <template-directory> --archive-inventory <metadata-inventory.json> --output docs/static/data/task-library.json`, then run `build_evidence.py` to update content-version URLs. The generated index is self-contained for the public site; raw local files are not uploaded. Metadata inventory excludes source, config, credentials, prompts, inputs, caches, and media. Saved ICL `{config, results}` files are included as experiment results.

## Example selection

**Examples** keeps 96 cases in the same editor and feedback panes. LlamaGuard, Toxic-BERT, and PyOD appear first, followed by news classification, Detoxify, Qwen3Guard, sentiment, moderation, and web-chat screenshots. The picker searches example titles, task text, tool names, and LLM names. Readers can select with the mouse or arrow keys and Enter, use the previous/next buttons, or play through a task's examples. Opening the picker pauses playback; Escape restores the current choice.

The **Text** view presents articles in a serif face, responses in a sans-serif face, and paired safe/unsafe responses as labeled blocks. **Code / Raw** shows the serialized excerpt in monospace. Terminal output uses monospace while agent messages use prose typography. This mode cycles archived examples without inventing a tool-execution sequence.

`static/data/workspace-outputs.json` retains source-file and context hashes, original relative paths, record pointers, and display changes for the 22 curated local outputs. Raw ignored output files are not uploaded. Name placeholders such as `President [Name]` are masked as `President ███` in displayed excerpts.

Every case retains its source path. The 33 Chat API examples come from saved Grok 4.1 Fast, Claude Sonnet 4.5, and DeepSeek V3.2 records. Grok and Sonnet use the archive's extracted-response field; DeepSeek uses JSON response fields parsed from the saved reply. Source record IDs and pointers remain available.

`static/data/additional-cases.json` adds 12 Toxic-BERT excerpts, 12 PyOD excerpts, four news examples, and one sentiment example. The main-experiment excerpts come from the local `NIPS-ISC-Code-Share` archive and retain relative paths, source hashes, record IDs, and extraction locations. Their public source links point to this curated excerpt file, because the full raw runs are not published here. Toxic-BERT uses `unitary/toxic-bert` with a strict score threshold of `> 0.5`; PyOD requires an outlier as the last sample and normal reference samples. These are single-turn responses, not executed agent trajectories. A further Detoxify dataset is taken from the existing toxicity workflow's final saved data.

Opus 4.6 Thinking generates prompts for named methods; GPT-5.2 generates responses to supplied prompts. Their moderation flags are not presented as a measured jailbreak of an independent target LLM. The notebook entry is explicitly a follow-up instruction with saved outputs available at its source.

Screenshots come from the paper's redacted six-panel figure, copied from `assets/optimized/paper-v2-web-examples.webp`; CSS displays individual panels. Generated excerpts are redacted before publication in JSON, rather than hidden behind a CSS overlay. Sensitive details are masked and excerpts shortened.

## Reported triggers and media

Below the workspace, searchable cards mirror all 62 reported LLM entries and evidence URLs from the English README. This is an archive index, not a ranking or a claim that every setup succeeds. Task-library and experiment links remain available. The previous explanatory application panels are removed so the page concentrates on outputs and reported results.

The feedback pane shows the text being written or checked alongside the recorded result. These excerpts come from the same frame as the editable-data view; blank fields are not presented as generated content. Safe/unsafe response pairs retain separate labels.

The MP4 uses the existing GitHub attachment and `preload="none"`. `video-poster.jpg` is a still from the existing repository video. No new MP4 is added. Fonts load from Google Fonts (Fraunces, Urbanist, Geist Mono) and fall back to local system stacks. The browser loads one compressed screenshot image and curated JSON data. Citation details are collapsed at the bottom.

## Adding evidence

Add public-source cases in `build_evidence.py`, curated source excerpts in `static/data/additional-cases.json`, and chronological workflows in `build_workflows.py`. Attach agent activity in `build_agent_activity.py`, extract chat trajectories in `build_chat_trajectories.py`, or add presentation sequences through `build_workspace_walkthroughs.py`, then rebuild. Check each frame against its source entry. Preserve the distinction between generated data, in-memory probes, complete validation runs, and editorial summaries. Use recorded output for result claims; label task templates as templates. Keep corrective context when shortening responses. Do not include credentials or unredacted operational details.
