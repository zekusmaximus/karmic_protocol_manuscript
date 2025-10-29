Revised Full Manuscript Export

Purpose
- Holds one Markdown file per scene in the new publication order defined by `order.csv`.
- Filenames are prefixed with a zero-padded index and include chapter/scene for reference, e.g. `001_ch01_s01.md`.

How it’s generated
- Source of truth: `order.csv` (columns: `chapter,scene,pov,location,file,notes`).
- Export script: `scripts/copy_revised_full.py`.
- The script:
  - Reads `order.csv` in row order (top to bottom = reading order).
  - Uses each row’s `file` as the source (prefers `revised_scenes/` if you set it).
  - Strips any YAML header from the source file.
  - Writes to `revised_full/{index}_ch{chapter}_s{scene}.md`.

Update workflow
1) Edit `order.csv` to:
   - Point `file` to revised scenes (e.g., `revised_scenes/ch03_s01.md`).
   - Adjust `chapter`/`scene` to your desired numbering.
   - Keep rows sorted in desired publication order.
2) Rebuild the export:
   - `python scripts/copy_revised_full.py`

Related scripts
- `scripts/extract_order.py`: Generate `order.csv` from `full_manuscript.md` (auto-prefers `revised_scenes/` paths where present).
- `scripts/assemble_from_csv.py`: Build `full_manuscript.generated.md` from `order.csv` for a full-preview read.

Notes
- This directory is regenerated; the script removes existing `.md` files before writing.
- Source scene files remain unchanged; only YAML headers are stripped on export.
