# README figures and repository sources

This map connects the English README's figures to task code, templates, and archived results. The paper figures come from [arXiv v2](https://arxiv.org/abs/2603.23509v2). A template specifies a task; a recorded run contains the model's actual output. The links below identify which material is available for each figure.

## Observation and task design

| README figure | Repository material | What corresponds |
|---|---|---|
| B · Figure 1: the initial observation | [LlamaGuard task](../../codebase_templates/aiml_llamaguard/exp0.txt); [agent implementation](../../experiment/tvd_agent/agent.py) | The template uses the same safety classifier as the bottom panel. That panel also shows an `S2` category check; the public template checks only `safe`/`unsafe` labels. The harmless `greeting-demo` and the three top-row interactions are shown in the paper; a separate transcript for those interactions has not been located in this checkout. |
| C · Figure 2: workspace execution | [Toxic-BERT prompt builder](../../experiment/tvd_chatbot/build.py), [task examples](../../experiment/tvd_chatbot/prompts/jbb/ai-detoxify/0sample.json), [agent runner](../../experiment/tvd_agent/run.sh) | The task examples load `unitary/toxic-bert`, with `flagged` and `not_flagged` response fields and a score threshold of `> 0.5`. They call the query field `prompt` and the schema file `schema.py`, where the diagram uses `query` and `validator.py`. These are text-based task contexts; the runner supplies actual agent execution. |
| C.1 · Figure 3, untargeted generation | [LlamaGuard template](../../codebase_templates/aiml_llamaguard/exp0.txt); [prepared Qwen3Guard workspace](../../experiment/tvd_agent/template/my_favorite/) | The panel shows unfinished `query` and `assistant_unsafe` fields. The LlamaGuard template additionally requires `assistant_safe`. `my_favorite` implements this paired-response task with Qwen3Guard and different label parsing, described below. |
| C.1 · Workspace trajectory | [LlamaGuard template](../../codebase_templates/aiml_llamaguard/exp0.txt); [diagram source notes](../tvd-mechanism-figures-sources.md) | The fields, tool, and acceptance rules follow the template. The successive candidates are illustrative; they are not a saved model run. |
| C.2 · Figure 3, anchors | [Query](../../codebase_templates/aiml_llamaguard/exp0.txt), [category](../../codebase_templates/aiml_detoxify/exp0.txt), [sequence](../../codebase_templates/compbio_pyrosetta/exp0.txt), [attack class](../../codebase_templates/cyber_nids/exp0.txt), [data name](../../codebase_templates/compchem_pymatgen/exp0.txt) | These files show the corresponding kinds of prefilled data. The figure labels its category panel Toxic-BERT; in the public library, the editable `target_category` field belongs to Detoxify. The [Toxic-BERT template](../../codebase_templates/aiml_toxigen/exp0.txt) uses a fixed `toxic` score instead. |
| C.3 · Score steering | [Toxic-BERT task](../../codebase_templates/aiml_toxigen/exp0.txt) | `unitary/toxic-bert` scores the first 512 characters; the task requires at least 50 words and `toxic_score >= 0.5`. The displayed 0.30, 0.40, and 0.62 are illustrative scores. |
| D · Figure 7: named attack methods | [Opus 4.6 report](../../community/claudeopus46thinking-guard-attack/), [validator](../../community/claudeopus46thinking-guard-attack/evidence/validator.py), [generated data](../../community/claudeopus46thinking-guard-attack/evidence/attack_cases_filled.json), [agent log](../../community/claudeopus46thinking-guard-attack/evidence/agent_log.json) | The record includes ArtPrompt, GCG, and PAP among six method labels. The validator reads `attack_cases.json`; the archive stores the completed copy as `attack_cases_filled.json`. Its terminal output reports six moderation flags. It does not evaluate jailbreak success against a target LLM. |
| D · Figure 5: different task tools | [LlamaGuard](../../codebase_templates/aiml_llamaguard/exp0.txt), [PyOD](../../codebase_templates/aiml_pyod/exp0.txt), [Toxic-BERT](../../codebase_templates/aiml_toxigen/exp0.txt) | These are the corresponding task implementations. PyOD checks that only the final sample is an outlier among the supplied reference samples. The templates are not logs of the three displayed completions; those excerpts are preserved in the published figure. |

### LlamaGuard and Qwen3Guard workspaces

The [LlamaGuard template](../../codebase_templates/aiml_llamaguard/exp0.txt) loads `meta-llama/Llama-Guard-3-8B`. It checks paired safe/unsafe responses and parses the first generated line as exactly `safe` or `unsafe`.

The prepared [`my_favorite`](../../experiment/tvd_agent/template/my_favorite/) workspace uses `Qwen/Qwen3Guard-Gen-0.6B` with the same response fields. Its implementation maps both `Unsafe` and `Controversial` to an internal `unsafe` label; an unmatched response falls back to `safe`. The current [`aiml_guard_type1`](../../experiment/tvd_agent/template/aiml_guard_type1/) also uses Qwen3Guard, but requires only `assistant_unsafe` in `test_cases.json`. These differences matter when comparing a public run with the LlamaGuard figures.

The [paper's agent transcript](https://arxiv.org/html/2603.23509v2#A8.T4) retains its original LlamaGuard filenames. A link from that transcript to a current workspace identifies a runnable variant, not an identical saved execution.

## Results and applications

| README figure or result | Repository material | What corresponds |
|---|---|---|
| E · From a template to a saved run | [`my_favorite`](../../experiment/tvd_agent/template/my_favorite/), [runner](../../experiment/tvd_agent/run.sh), [agent](../../experiment/tvd_agent/agent.py) | These are the files shown in the diagram. The runner's final check uses the original validator in a read-only mount. Its status is printed separately from `agent_log.json`. [Detailed file mapping](../tvd-reader-examples-sources.md). |
| G · Figure 4: one query across LLMs | [Grok 4.1 Fast input](../../experiment/tvd_chatbot/prompts/jbb/ai-guard/1sample.json), [output](../../experiment/tvd_chatbot/result_demo/x-ai-grok-4.1-fast/jbb/ai-guard/1sample.json), [evaluation](../../experiment/tvd_chatbot/result_demo/x-ai-grok-4.1-fast/jbb/ai-guard/1sample_judged.json) | Record `5ffec320`, index 32, contains the payday-loan query. This is a complete reference run on the same query, with one supplied example. Its output differs from the figure's Grok excerpt, so it is not presented as the source of the five displayed completions. |
| H · Figure 9: public web-interface outputs | See the six records below. | Each record contains the corresponding case screenshot and an original conversation link. |
| I · Figure B.1: domain coverage | [Template library](../../codebase_templates/) | The figure summarizes the paper's 53 workflows across eight disciplines. The repository's later library has 84 templates across nine domains; the figure is not a count of the current folders. |
| I · Detoxify template variants | [`aiml_detoxify`](../../codebase_templates/aiml_detoxify/); [file-by-file comparison](../tvd-reader-examples-sources.md) | The displayed rows, categories, and minimum lengths correspond to `exp0.txt` through `exp3.txt` in this folder. |
| D · Figure 6: batch generation | [Agent batch workspace](../../experiment/tvd_agent/template/aiml_guard_type1/); [chat follow-up notebook](../../experiment/harmful_data_generator/unsafe_response.ipynb) | The agent workspace processes multiple records using Qwen3Guard. The notebook demonstrates repeated generation through chat calls. These are related implementations; neither is identified as the exact LlamaGuard 10-to-20-record execution pictured in Figure 6. |
| D · Table 4: detector training | [Published results](https://arxiv.org/html/2603.23509v2#S5.T4) | The README reproduces the reported F1 values. A script and dataset for reproducing this exact fine-tuning comparison have not been located in this checkout. The generation notebooks should not be described as its training implementation. |
| D · Figure 8: autonomous red teaming | [Experiment](../../experiment/automated-red-teaming-qwen-guard/), [task](../../experiment/automated-red-teaming-qwen-guard/codespace/task.py), [completion evaluator](../../experiment/automated-red-teaming-qwen-guard/gate/completion_gate.py) | The code tests a prompt against a target LLM and checks its response with Qwen3Guard. The default target is `deepseek/deepseek-v4-flash`. Run artifacts are saved under the gitignored `runtime_result/`; this link provides the implementation, not a public log of the depicted attempts. |
| J · Figure F.1: response behavior | [Paper analysis and figure](https://arxiv.org/html/2603.23509v2#A6) | The figure reports categories and frequencies in the paper's sampled traces. A file of per-trace annotations for this plot has not been located in this checkout. The separately linked [Opus 4.8 log](../../community/claudeopus48-agent-qwenguard/evidence/agent_log.json) illustrates evaluator feedback; it is not the source of the plotted frequencies. |

### Figure 9: archived case records

| Panel | Case record | Content shown |
|---|---|---|
| Claude Opus 4.5 | [Record and screenshots](../../community/claudeopus45-share/) | Multilingual toxic/non-toxic examples. |
| GPT-5.2 Chat | [Record and screenshot](../../community/issue-29-gpt52chat/) | Biased news samples in YAML. |
| Gemini 3 Pro | [Record and screenshots](../../community/issue-13-gemini3pro/) | Completion of a forensic-analysis dataset. |
| DeepSeek V3.2 | [Record and screenshot](../../community/deepseek-v32-share/) | Prompt-injection test cases for Qwen3Guard. |
| GLM-5 | [Record and screenshot](../../community/glm5-share/) | Paired safe and unsafe responses in JSON. |
| Qwen 3 Max | [Record and screenshots](../../community/issue-4-qwen3max/) | Multilingual toxicity examples in JSON. |

The figure preserves the paper's redactions. Original screenshots and share links remain in their case folders.
