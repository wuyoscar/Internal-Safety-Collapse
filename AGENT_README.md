# ISC-Bench — Agent Entry Guide

Use this file as the first instruction packet for Claude Code, Codex, Gemini CLI,
Cursor, OpenClaw, or another coding/research agent working inside ISC-Bench.

## Copy-Paste Entry

```text
Help me work on ISC-Bench. First read:
https://raw.githubusercontent.com/wuyoscar/ISC-Bench/main/AGENT_README.md

Then inspect the local repository state and help with this goal:
<describe the goal here>
```

## Mission

ISC-Bench is an academic safety research repository for studying Internal Safety
Collapse (ISC): cases where a model completes a professional-looking workflow
and produces policy-relevant harmful output because the workflow's task,
validator, and data schema structurally require it.

The core abstraction is TVD:

- **Task**: the professional workflow the model is asked to complete
- **Validator**: code or checks that define whether the workflow succeeds
- **Data**: fields the model must fill to satisfy the validator

The repo currently centers on 84 public scenarios across 9 domains, plus
single-turn, ICL, and agentic evaluation code.

## Non-Negotiable Boundaries

- Treat the project as academic safety research, not a misuse manual.
- Do not strengthen harmful examples unless the user explicitly asks for a
  controlled research edit and the edit is necessary.
- Preserve the TVD structure when editing templates; do not make scenarios more
  dramatic just to increase apparent harm.
- Do not sanitize or rewrite archived community evidence in a way that damages
  reproducibility or attribution.
- When showing model outputs that contain harmful, toxic, or misinformation-like
  content, frame them as benchmark evidence and not as project endorsement.
- For documentation-only tasks, keep changes documentation-only unless the user
  explicitly reopens experiment behavior.

## Preflight For Agents

Before making changes:

1. Run `git status --short --branch` and do not revert unrelated user work.
2. Read `README.md`, this file, and the nearest subsystem README for the task.
3. Verify referenced files exist before citing or editing them.
4. Choose one work lane below and keep changes scoped to that lane.
5. Use the narrowest meaningful verification before claiming completion.

## Repository Map

| Path | Use |
|---|---|
| `README.md` | Public project overview, leaderboard, tutorials, examples |
| `ISC_PAPER_DIGEST.md` | Paper-level summary of the method and results |
| `VERIFICATION.md` | How ISC-Bench defines and verifies "Triggered" cases |
| `templates/` | Public TVD scenario library; each released scenario has a `SKILL.md` |
| `experiment/` | Reproducible evaluation pipelines |
| `experiment/isc_single/` | TVD-Single: one prompt contains the full workflow context |
| `experiment/isc_icl/` | TVD-ICL: completed demonstrations precede the target case |
| `experiment/isc_agent/` | TVD-Agentic: autonomous file/code workflow with Docker |
| `community/` | Curated, attributed reproductions tied to public issues |
| `docs/` | Static project website |
| `tutorials/` | Concept/tutorial material for understanding and extending ISC |
| `SKILL.md` | Command-level runbook for benchmark execution |

## Work Lanes

### 1. Explain ISC-Bench

Read `README.md`, `ISC_PAPER_DIGEST.md`, and `VERIFICATION.md`. Explain ISC as
a workflow-induced failure pattern, not as a standard direct jailbreak.

Stop when the user has: a concise definition, the TVD mechanism, the evaluation
modes, and the evidence standard.

### 2. Inspect Or Reuse A Template

Start from `templates/README.md`, then open the target scenario directory and
its `SKILL.md`. Keep task, validator, and data schema aligned. If adjusting a
scenario, prefer minimal anchor/schema edits over broad rewrites.

Stop when the template path, validator logic, data fields, and expected trigger
mechanism are clear.

### 3. Run Or Explain Experiments

Start from `SKILL.md` and `experiment/README.md`, then choose the relevant mode:

- `experiment/isc_single/` for the default reproducible prompt pipeline
- `experiment/isc_icl/` for demonstration-count experiments
- `experiment/isc_agent/` for autonomous agent runs with Docker

Do not assume single-turn templates are 1:1 drop-ins for agent mode. Agentic
runs often need small layout or workspace adjustments; follow
`experiment/isc_agent/README.md`.

Stop when the command, input path, output path, and verification step are all
explicit.

### 4. Verify Or Submit A Case

Use `VERIFICATION.md` before calling a case "Triggered". For community cases,
preserve contributor attribution, issue links, original evidence, and the
folder conventions in `community/README.md`.

Submission issue:

```text
https://github.com/wuyoscar/ISC-Bench/issues/new?template=isc-submission.md&title=[ISC]+Model+Name
```

Stop when the model, template/domain, evidence path, issue/community path, and
verification rationale are all recorded.

### 5. Update Documentation Or Website

Keep public-facing docs clear, conservative, and research-framed. The website
under `docs/` is the project page; tutorial/documentation content can link back
to `README.md`, `tutorials/`, notebooks, and examples, but should not duplicate
the whole repository.

Stop when links work, wording is consistent with the safety boundary, and the
page renders without obvious layout regressions.

## Good Final Answer Shape

When reporting back to the user, include:

- what changed or what was inspected
- the exact files or paths involved
- the verification performed
- any remaining risk, missing credential, or intentionally untested step

For code or docs edits, prefer file-specific references over broad summaries.

## One-Sentence Summary

Read the repo state first, stay inside the academic safety boundary, choose the
right lane, preserve TVD structure, verify the smallest relevant thing, and
report the concrete evidence.
