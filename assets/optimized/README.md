# README display images

The READMEs load the files below. Paper figures are WebP previews of the published figures; the project's own illustrations are rendered from HTML; the two animations are recordings of the project page.

## Paper figures

The `paper-v2-*` previews are described in [paper-v2/README.md](../paper-v2/README.md). Each one links to its figure in the published paper. They use lossless WebP at 2000 pixels wide and are regenerated with `assets/paper-v2/render.py`.

## Figures rendered from HTML

| Preview | Shows |
|:---|:---|
| `readme-workspace-trajectory.webp` | One LlamaGuard workspace across three attempts. An illustrative sequence, not an experimental trace. |
| `readme-score-steering.webp` | The fixed `>= 0.5` Toxic-BERT check, with explicitly illustrative scores. |
| `readme-agent-run.webp` | File roles and paths in the `my_favorite` Docker run. |
| `readme-template-variants.webp` | The four `aiml_detoxify` template variants. |

Their sources are HTML files in `../readme-figures/`, styled with the project page's colours and typefaces. Each preview links to `../readme-<name>.png`. Field names, checks, and error messages come from the files listed in [tvd-mechanism-figures-sources.md](../tvd-mechanism-figures-sources.md) and [tvd-reader-examples-sources.md](../tvd-reader-examples-sources.md). Rebuild all four with:

```sh
uv run assets/readme-figures/render.py
```

## Project page recordings

`../site-hero.webp` (top of the READMEs) and `../site-tools.webp` (section D · V) are animated WebP recordings of the project page, 1600 px wide: twice the width a README shows them at, so text stays sharp on high-density displays. Serve `docs/` on port 8098, then record both with:

```sh
uv run assets/readme-figures/record_site.py
```

## Model icons

Model icons shared by the README and project website live in `docs/static/img/favicons/`; `sources.json` records their original URLs.

## Earlier files kept for reference

The READMEs no longer load these. They stay in the repository so that older links keep working.

- `tvd-*.drawio.png` with their `tvd-*.webp` previews: earlier draw.io illustrations (execution modes, workspace trajectory, query steering, score steering, prompt generation, agent run files, template workspaces, tool generality). Each PNG embeds its editable draw.io XML.
- `tvd_mechanism`, `fig1_bench_overview`, `fig2_tvd_framework`, `fig3_cross_domain`, `cross_domain_panel`, `tvd-behavior-taxonomy`, `web_llms`: figures from earlier versions of the paper and README; the READMEs use their v2 counterparts.

To rebuild a preview after editing one of the draw.io PNGs:

```sh
cwebp -lossless -z 9 -exact -metadata all -resize 2000 0 -mt assets/<name>.drawio.png -o assets/optimized/<name>.webp
```
