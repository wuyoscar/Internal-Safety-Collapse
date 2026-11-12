# README display images

The README loads WebP previews. The current paper figures use the `paper-v2-*` files described in [paper-v2/README.md](../paper-v2/README.md); their links open the corresponding figures in the published paper. The custom workspace illustrations link to their editable PNG sources. Keep the older originals for historical references.

All WebP outputs use lossless encoding. The mechanism and overview previews are resized to 2000 pixels wide for the README. Some historical framework and example-panel exports retain their original dimensions and decoded pixels. The v2 figures use the separate rendering script linked above.

Regenerate an output when its source changes, using `cwebp`:

```sh
cwebp -lossless -z 9 -exact -metadata all -resize 2000 0 -mt assets/tvd_mechanism.png -o assets/optimized/tvd_mechanism.webp
cwebp -lossless -z 9 -exact -metadata all -resize 2000 0 -mt assets/fig1_bench_overview.png -o assets/optimized/fig1_bench_overview.webp
cwebp -lossless -z 9 -exact -metadata all -mt assets/fig2_tvd_framework.png -o assets/optimized/fig2_tvd_framework.webp
cwebp -lossless -z 9 -exact -metadata all -mt assets/trigger_example/cross_domain_panel.png -o assets/optimized/cross_domain_panel.webp
```

Model icons shared by the README and project website live in `docs/static/img/favicons/`; `sources.json` records their original URLs.

The earlier `tvd-execution-modes.webp` was exported from `../tvd-execution-modes.drawio.png`, which embeds an editable draw.io diagram. It and the older `tvd_mechanism` files remain available for historical reference. The README now uses the published v2 overview and untargeted-generation figures, alongside the custom workspace trajectory.


The README's workspace illustrations use the same editable draw.io format:

- `tvd-execution-modes.webp`: LlamaGuard task and data file; the unsafe response passes only when LlamaGuard labels it unsafe.
- `tvd-workspace-trajectory.webp`: an illustrative sequence of edits and checks, not an experimental trace.
- `tvd-template-workspaces.webp`: real repository folders and context-file variants.

Each preview links to `../<name>.drawio.png`, which embeds the editable XML. After editing and exporting that PNG in draw.io, rebuild its preview with:

```sh
cwebp -lossless -z 9 -exact -metadata all -resize 2000 0 -mt assets/<name>.drawio.png -o assets/optimized/<name>.webp
```

The earlier paper assets `fig1_bench_overview.png` and `fig2_tvd_framework.png` remain available for historical references; the README uses their v2 counterparts. The LlamaGuard illustrations show the guard evaluating both responses inside the task; the executable `my_favorite` template uses Qwen3Guard.


Additional B-section illustrations use the same PNG-with-embedded-XML and WebP preview pair:

- `tvd-query-steering`: a blank query versus a supplied query in the LlamaGuard data shape.
- `tvd-score-steering`: the fixed `>= 0.5` toxicity check, with explicitly illustrative scores.
- `tvd-prompt-generation`: the adversarial-prompt task objective, its two acceptance conditions, and failed/revised candidates in the Qwen3Guard red-teaming workspace. Candidate content is omitted.

These are explanatory drawings, not screenshots of newly executed experiments. Their field names and conditions come from the source links beside each README figure.


## Figures rendered from HTML

`readme-agent-run.webp`, `readme-template-variants.webp`, `readme-workspace-trajectory.webp` and `readme-score-steering.webp` replace the earlier `tvd-agent-run-files`, `tvd-template-workspaces`, `tvd-workspace-trajectory` and `tvd-score-steering` illustrations in the READMEs. The earlier draw.io files remain for reference. Their sources are HTML files in `../readme-figures/`, styled with the project page's colours and typefaces. Each preview links to `../readme-<name>.png`. Rebuild all four with:

```sh
uv run assets/readme-figures/render.py
```

`../site-tour.gif` at the top of the READMEs is a recording of the project page (hero player, tool stage, template belt) at 880 px wide and 10 frames per second.

