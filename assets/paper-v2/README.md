# Figures from the published paper (v2)

These previews come from [arXiv:2603.23509v2](https://arxiv.org/abs/2603.23509v2), published on 5 November 2026. The figure files were checked against the public [TeX source bundle](https://arxiv.org/src/2603.23509v2). The README displays them inline and links each to its figure in the paper.

`manifest.json` records the source filename and SHA-256, the preview dimensions and SHA-256, and the source figure link. PDF figures are rendered at 2000 pixels wide. The web-interface examples are resized to 2000 pixels wide, preserving the complete panel and its existing redactions. The linked paper retains the original figures. All previews use lossless WebP encoding.

Regenerate the previews from an extracted copy of the public source bundle:

```sh
python assets/paper-v2/render.py /path/to/extracted/arxiv-v2-source
```

This requires PyMuPDF and Pillow. The script reads the source files without changing them, writes previews under `assets/optimized/`, and verifies that WebP encoding preserves the rendered pixels.

| Source figure | README placement |
|---|---|
| Figure 1: chatbot and coding-agent behavior | C: Agent experiments |
| Figure 2: ISC task execution | B: How it works |
| Figure 3: anchors and untargeted generation | B.1 and B.2 |
| Figure 4: the same query across LLMs | E: Model results |
| Figure 5: the same query across task tools | B.5: Generality |
| Figure 6: batch generation | H: Downstream applications |
| Figure 7: method-specific prompt generation | B.4 |
| Figure 8: iterative red teaming | H: Downstream applications |
| Figure 9: public web-interface examples | F: Example outputs |
| Figure B.1: domain coverage | G: Paper experiments |
| Figure F.1: response behavior | I: Awareness of ISC |

The detector-training results in H reproduce Table 4's F1 values. They are separate from the task-validation examples in the figures. The older post-training comparison still links explicitly to v1, where that experiment was reported.
