#!/usr/bin/env python3
"""
Create revised_full/ with one file per scene in the new order.

Source order comes from order.csv. Each row's 'file' is used as the source.
Destination filenames are prefixed with a zero-padded order index to preserve
reading order, followed by chXX_sYY for easy reference, e.g.:

  revised_full/001_ch01_s01.md

Existing .md files in revised_full/ will be removed before export to avoid
stale files.
"""

import csv
from pathlib import Path

ROOT = Path('.')
ORDER_CSV = ROOT / 'order.csv'
OUTDIR = ROOT / 'revised_full'


def load_rows():
    rows = []
    with ORDER_CSV.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize header BOM if present
        if reader.fieldnames:
            reader.fieldnames = [fn.lstrip('\ufeff').strip() if fn else fn for fn in reader.fieldnames]
        for i, row in enumerate(reader, start=1):
            if not any(row.values()):
                continue
            ch = int((row.get('chapter') or '').strip())
            sc = int((row.get('scene') or '').strip())
            src = (row.get('file') or '').strip()
            pov = (row.get('pov') or '').strip()
            loc = (row.get('location') or '').strip()
            rows.append({'idx': i, 'chapter': ch, 'scene': sc, 'file': src, 'pov': pov, 'location': loc})
    return rows


def strip_yaml(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == '---':
        try:
            end = 1 + lines[1:].index('---')
            lines = lines[end+1:]
        except ValueError:
            pass
    return '\n'.join(lines).strip() + '\n'


def main():
    rows = load_rows()
    OUTDIR.mkdir(exist_ok=True)
    # Clean old .md files
    for p in OUTDIR.glob('*.md'):
        p.unlink()

    width = max(3, len(str(len(rows))))
    for pos, row in enumerate(rows, start=1):
        ch = row['chapter']
        sc = row['scene']
        src = Path(row['file'])
        if not src.exists():
            raise SystemExit(f"Missing source file: {src}")
        content = src.read_text(encoding='utf-8')
        # Export content as-is (no YAML), to keep revised scenes clean
        out_text = strip_yaml(content)
        out_name = f"{pos:0{width}d}_ch{ch:02d}_s{sc:02d}.md"
        dest = OUTDIR / out_name
        dest.write_text(out_text, encoding='utf-8')
    print(f"[OK] Exported {len(rows)} scenes to {OUTDIR}/")


if __name__ == '__main__':
    main()

