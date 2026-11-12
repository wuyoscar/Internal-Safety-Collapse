# README mechanism figures: sources and display conventions

> The READMEs now show `readme-workspace-trajectory` and `readme-score-steering`, redrawn from HTML in `assets/readme-figures/` using the sources below. The `tvd-*.drawio.png` files named here are the earlier versions.

The six workspace diagrams use native draw.io elements embedded in their `.drawio.png` files. Their WebP display copies are lossless. They illustrate task structure and agent actions using the source contracts below.

## Display conventions

- `???` is an unfinished field in the task data.
- `[xxx]` and ellipses shorten the displayed example. They are not a complete candidate submitted to a classifier. Visible beginnings such as “How to make [xxx]?” and “Step 1: [xxx]” convey the roles of the fields without including an operational harmful example.
- Illustrative labels and scores describe full hypothetical candidates, including any required length. The shown beginnings do not independently establish those labels or scores.
- R means read-only; W means editable. Permissions follow the specific source, rather than assuming that every validator file is read-only.
- Code and terminal panels may be summarized for display. A panel is not an exact transcript unless identified as a recorded excerpt.

## Color and typography semantics

- Sage green indicates a safe label or a response treated as safe within the illustrative evaluation. Terracotta indicates an unsafe label or a risk signal such as a moderation flag or toxicity above the task threshold.
- Muted plum `✓ PASS` and ochre `× FAIL` describe task acceptance separately. An unsafe response can therefore retain its terracotta label while the task displays a plum pass. No passing row is painted green as a whole.
- Field names such as `assistant_unsafe` remain neutral and bold: they describe the required slot. When that slot contains a safe refusal, its text background and returned `safe` label stay green, alongside an ochre task failure.
- Unfinished or unevaluated content uses gray. A lack of a moderation flag alone is not treated as a safe classification.
- Text remains explicit, with labels and status symbols alongside colors. Headers and important fields use bold sans-serif/monospace type; dark panels have white body text and lighter semantic accents. Native, editable outer shadows distinguish workspace cards from the background.
- The tool-family panels in the generality figure use neutral backgrounds; their headings and file labels remain charcoal.
- Typography separates content roles: Menlo for filenames, paths, data and terminal/code text; Helvetica Neue for explanations and agent actions; bold Helvetica Neue for headings and conclusions. Mixed captions use inline font runs so a filename and its description remain visibly different. Permissions and prose about saved files use sans-serif text.
- Python keywords use muted berry, calls and classes use teal, and strings (including complete model IDs) use copper. JSON keys remain charcoal and values use string coloring. These syntax colors are separate from the safe/unsafe classifications and task acceptance colors.
- Folder outlines, document icons, file tabs and child indentation distinguish workspace structure from file contents. Code and data use light editor panels; tool output retains a charcoal terminal background.

## Diagram sources

| Figure | Source and preserved contract |
|---|---|
| `tvd-execution-modes.drawio.png` | `codebase_templates/aiml_llamaguard/exp0.txt`: run `llama_guard.py`; JSON array with id/query/assistant_safe/assistant_unsafe; query ≥10 characters, responses ≥100 words; safe/unsafe label checks. Only `llama_guard.py` is read-only in this source transcript. |
| `tvd-workspace-trajectory.drawio.png` | Same LlamaGuard schema. Initial missing fields, an illustrative safe substitute in the unsafe slot, then an illustrative revised response. These are not measured model outputs or a guarantee of convergence. |
| `tvd-query-steering.drawio.png` | Same schema, contrasting agent-chosen and researcher-supplied queries. Field excerpts are abbreviated. The source does not enforce query preservation or answer relevance. |
| `tvd-score-steering.drawio.png` | `codebase_templates/aiml_toxigen/exp0.txt`: `unitary/toxic-bert`; no unfinished fields; ≥50 words; classifier receives the first 512 characters; `toxic_score >= 0.5`. Displayed 0.30/0.40/0.62 scores are illustrative. |
| `tvd-prompt-generation.drawio.png` | `experiment/automated-red-teaming-qwen-guard/codespace/{task.py,tvd_validator.py}` and `gate/completion_gate.py`: prompt ≥40 words; moderation flags the input; target response judged `Safety: Unsafe` and `Refusal: No`. Only data.json is the intended editable input. `rounds.json` records attempts after loading valid JSON; missing files or invalid JSON exit earlier. Reply length is recorded, not an independent success rule. |
| `tvd-tool-generality.drawio.png` | See `tvd-tool-generality-sources.md` for Hugging Face classifier templates, the pymatgen materials-science template, and HarmProfile. Its panels describe task structure and illustrative feedback, without claiming recorded agent runs. |

## Layout references

All diagrams retain the README's established file-editor and terminal style. Layout references from Oscar's Figure Atlas were inspected:

- `OpenHands_2407.16741_fig2_trajectory_event_stream.png`: compact action/observation records with runtime context.
- `CyberArena_2610.19005_appfig15_pastel_interface_panels.png`: concrete interface fields, restrained panels, and local explanatory labels.
- `AppWorld_2407.18901_fig1_trajectory_chat_code.png`: code syntax colors separated from surrounding explanation and tool output.
- `MagenticOne_2411.04468_fig1_agent_trajectory_numbered_steps.png`: recognizable file, coder and terminal roles within numbered workspace panels.

Only layout principles were used. The diagram wording, examples, file views, and native elements were authored for ISC.

## Notes retained outside the redesigned figures

The visual redesign preserves the body content and moves these small footer notes out of the images.

- **`tvd-execution-modes`**: ??? = unfinished data · [xxx] = display truncation. Labels refer to full illustrative responses. The runnable my_favorite workspace uses Qwen3Guard; this schematic follows the LlamaGuard template.

- **`tvd-workspace-trajectory`**: ??? = unfinished data · [xxx] = truncated display text. Full responses satisfy the length checks. Labels illustrate the full candidates; this is not a measured run. Actual runs can refuse or stop.

- **`tvd-query-steering`**: ??? = unfinished data · [xxx] = display truncation. Examples and labels are illustrative. A supplied query is an input. The source guard does not check that it is preserved or that the response answers it.

- **`tvd-score-steering`**: [xxx] and ellipses shorten the displayed text; each full entry meets the 50-word check. The threshold remains 0.50, and exactly 0.50 passes. Real revisions can raise or lower the score.

- **`tvd-prompt-generation`**: [xxx] = display truncation. Full prompt candidates satisfy the 40-word check. Attempts and target replies are illustrative; the checks and output files follow the implementation.

- **`tvd-tool-generality`**: Illustrative output excerpts · [xxx] marks display truncation. Tool requirements apply to complete candidates. CIF fields show the form of the generated structure data. Full code and model-access details are linked in the README.

The figures use larger type, compact spacing, warm-white panels, charcoal borders, restrained semantic colors and native outer shadows. Layout references: `AdaExploreBench_2610.25950_fig1_three_row_numbered_cells_example_trajectory.png` and `BlenderWorld_2610.23986_fig2_four_stage_pastel_rubric_pipeline.png` from Oscar’s Figure Atlas; their grouped panels informed the redesign without copying their content.
