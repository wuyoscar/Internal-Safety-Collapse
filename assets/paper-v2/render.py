#!/usr/bin/env python3
"""Render the selected arXiv v2 figures for the README.

Usage: python assets/paper-v2/render.py /path/to/extracted/arxiv-v2-source
Dependencies: PyMuPDF, Pillow. Source files are read without modification.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image

FIGURES = {
    'motivation': ('fig_motivation.pdf', 'S1.F1'),
    'overview': ('fig_isc_overview.pdf', 'S2.F2'),
    'untargeted': ('fig_untargeted.pdf', 'S2.F3'),
    'anchors': ('fig_anchor.pdf', 'S2.F3'),
    'method-prompts': ('fig_red_team.pdf', 'S5.F8'),
    'tool-outputs': ('fig_cross_workflow.pdf', 'S3.F5'),
    'model-outputs': ('fig_same_query.pdf', 'S3.F4'),
    'web-examples': ('fig_web_cases.png', 'Sx1.F9'),
    'domains': ('fig_iscbench_overview.pdf', 'A2.F1'),
    'batch-generation': ('fig_batch.pdf', 'S5.F6'),
    'iterative-red-teaming': ('fig_red_team_iteration.pdf', 'S5.F8'),
    'behavior': ('fig_behavior.pdf', 'A6.F1'),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    assets = Path(__file__).resolve().parent.parent
    outputs = assets / 'optimized'
    outputs.mkdir(exist_ok=True)
    records = []
    for name, (filename, anchor) in FIGURES.items():
        source = args.source / 'fig' / filename
        if source.suffix == '.pdf':
            with fitz.open(source) as doc:
                page = doc[0]
                scale = 2000 / page.rect.width
                pixels = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                image = Image.frombytes('RGB', (pixels.width, pixels.height), pixels.samples)
        else:
            # Resize the full screenshot for display, retaining its existing redactions.
            with Image.open(source) as original:
                image = original.convert('RGB')
                image.thumbnail((2000, 20000), Image.Resampling.LANCZOS)
        output = outputs / f'paper-v2-{name}.webp'
        image.save(output, format='WEBP', lossless=True, method=6)
        with Image.open(output) as check:
            assert check.convert('RGB').tobytes() == image.tobytes()
        records.append({
            'name': name, 'source': 'fig/' + filename,
            'source_sha256': sha256(source),
            'preview': 'assets/optimized/' + output.name,
            'preview_sha256': sha256(output),
            'width': image.width, 'height': image.height,
            'bytes': output.stat().st_size,
            'paper_figure': f'https://arxiv.org/html/2603.23509v2#{anchor}',
        })
        print(f'{name}: {image.width} x {image.height}, {output.stat().st_size / 1024:.0f} KiB')
    (assets / 'paper-v2' / 'manifest.json').write_text(json.dumps({
        'paper': 'https://arxiv.org/abs/2603.23509v2',
        'source_bundle': 'https://arxiv.org/src/2603.23509v2',
        'encoding': 'lossless WebP', 'figures': records,
    }, indent=2) + '\n')
    print(f'Total: {sum(r["bytes"] for r in records) / 1024 / 1024:.2f} MiB')


if __name__ == '__main__':
    main()
