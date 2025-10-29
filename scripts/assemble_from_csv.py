#!/usr/bin/env python3
"""
Assemble a full manuscript from a CSV order plan.

Input: order.csv with columns: chapter,scene,pov,location,file,notes
Output: full_manuscript.generated.md

Notes:
- Files may include a YAML header bounded by '---' lines; this script strips it.
- Rows are sorted by (chapter, scene) numerically unless you pre-sort the CSV.
  To preserve a custom order, include the rows already sorted in the CSV.
"""

import csv
from pathlib import Path

OUTFILE = Path('full_manuscript.generated.md')


def read_csv(path='order.csv'):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize potential BOM and stray whitespace in header names
        if reader.fieldnames:
            reader.fieldnames = [fn.lstrip('\ufeff').strip() if fn else fn for fn in reader.fieldnames]
        for i, row in enumerate(reader, start=1):
            # Skip completely empty rows
            if not any(row.values()):
                continue
            try:
                # Allow for BOM on keys in some environments
                ch_key = 'chapter' if 'chapter' in row else next((k for k in row.keys() if k.endswith('chapter')), 'chapter')
                sc_key = 'scene' if 'scene' in row else next((k for k in row.keys() if k.endswith('scene')), 'scene')
                row['chapter'] = int((row.get(ch_key) or '').strip())
                row['scene'] = int((row.get(sc_key) or '').strip())
            except Exception:
                raise SystemExit(f'Bad chapter/scene number on line {i+1} in order.csv')
            rows.append(row)
    return rows


def read_scene_content(path: str) -> str:
    if not path:
        return ''
    p = Path(path)
    if not p.exists():
        raise SystemExit(f'Missing file: {path}')
    text = p.read_text(encoding='utf-8')
    # Strip YAML header if present (bounded by '---' at start and end)
    lines = text.splitlines()
    if lines and lines[0].strip() == '---':
        # find next '---'
        try:
            end = 1 + lines[1:].index('---')
            lines = lines[end+1:]  # skip final '---' and one blank line if present
        except ValueError:
            # malformed header; fall back to original lines
            pass
    return '\n'.join(lines).strip() + '\n'


def assemble(rows):
    # rows are assumed in desired order; if you want sorted, uncomment next line
    # rows = sorted(rows, key=lambda r: (r['chapter'], r['scene']))
    out = []
    current_ch = None
    for r in rows:
        ch = r['chapter']
        sc = r['scene']
        pov = r['pov'].strip()
        loc = r['location'].strip()
        file_path = r.get('file', '').strip()

        if current_ch != ch:
            out.append(f"=== CHAPTER {ch} ===\n")
            current_ch = ch

        out.append(f"[SCENE: CH{ch}_S{sc} | POV: {pov} | Location: {loc}]\n")
        content = read_scene_content(file_path)
        if not content:
            out.append('\n')
        else:
            out.append(content + '\n')

    OUTFILE.write_text(''.join(out), encoding='utf-8')
    print(f"[OK] Wrote {OUTFILE}")


if __name__ == '__main__':
    rows = read_csv('order.csv')
    assemble(rows)
