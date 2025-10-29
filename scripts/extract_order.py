#!/usr/bin/env python3
"""
Extract current scene order from full_manuscript.md into a CSV plan.

Output: order.csv with columns:
chapter,scene,pov,location,file,notes

The 'file' column is auto-filled if a matching file exists in
  - revised_scenes/chXX_sYY.md (preferred), else
  - scenes/chXX_sYY.md

Edit order.csv to change publication order, renumber chapters/scenes,
swap to revised files, or adjust POV/location. Then run assemble_from_csv.py.
"""

import csv
import re
from pathlib import Path

MANUSCRIPT = Path('full_manuscript.md')

chapter_re = re.compile(r'^=== CHAPTER (\d+) ===\s*$')
scene_re = re.compile(r'^\[SCENE: CH(\d+)_S(\d+) \| POV: (.+?) \| Location: (.+?)\]$')


def guess_file(ch: int, sc: int) -> str:
    cand_rev = Path('revised_scenes') / f'ch{ch:02d}_s{sc:02d}.md'
    cand_std = Path('scenes') / f'ch{ch:02d}_s{sc:02d}.md'
    if cand_rev.exists():
        return str(cand_rev).replace('\\', '/')
    if cand_std.exists():
        return str(cand_std).replace('\\', '/')
    return ''


def extract_rows():
    rows = []
    if not MANUSCRIPT.exists():
        raise SystemExit(f'Error: {MANUSCRIPT} not found')

    with MANUSCRIPT.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            m = scene_re.match(line.rstrip('\n'))
            if not m:
                continue
            ch = int(m.group(1))
            sc = int(m.group(2))
            pov = m.group(3).strip()
            loc = m.group(4).strip()
            rows.append({
                'chapter': ch,
                'scene': sc,
                'pov': pov,
                'location': loc,
                'file': guess_file(ch, sc),
                'notes': ''
            })
    return rows


def write_csv(rows):
    with open('order.csv', 'w', encoding='utf-8', newline='') as out:
        w = csv.DictWriter(out, fieldnames=['chapter', 'scene', 'pov', 'location', 'file', 'notes'])
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == '__main__':
    rows = extract_rows()
    write_csv(rows)
    print(f'[OK] Wrote order.csv with {len(rows)} rows')

