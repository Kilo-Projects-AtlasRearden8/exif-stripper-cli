# STATUS

## What was built

`exif-stripper`: a local-first Python CLI (Pillow only) that strips EXIF and GPS metadata from photos. It previews exactly which metadata fields will be removed before anything is saved, supports single-file and batch (`--batch`) processing, writes stripped copies next to originals or to a chosen output directory (or in place with `--in-place`), and can export a JSON report (`--report`). Everything runs offline — no cloud, no accounts, no network access.

Files:
- `exif_stripper.py` — the CLI (Pillow >= 10 dependency)
- `tests/test_exif_stripper.py` — metadata-removal, preview-as-dry-run, batch, in-place, PNG support, JSON-report, output-as-directory, and error-case tests
- `README.md` — plain-English usage guide crediting Asdale Dynamics, LLC
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `pyproject.toml` — installable package exposing the `exif-stripper` console script
- `.gitignore` — keeps compiled Python caches and build artifacts out of the repo

## How to run

```bash
python3 -m pip install Pillow          # or: pip install -e .   (adds `exif-stripper` command)
python3 exif_stripper.py --preview photo.jpg
python3 exif_stripper.py photo.jpg
python3 exif_stripper.py --batch --output cleaned/ --report report.json photos/
python3 -m pytest tests/
```

## Verification results

- `python3 -m pytest tests/`: **14 passed**, covering EXIF/GPS collection, stripping, pixel preservation (within JPEG lossy tolerance), preview-as-dry-run (no files modified), batch directory processing, in-place mode, PNG EXIF removal, report export, output-as-directory resolution, and error cases.
- `pip install -e .` installs successfully and exposes the `exif-stripper` console script.
- Manual end-to-end: preview correctly lists Make/Model/GPSInfo fields and prints "(preview mode: no files were modified)"; stripped output has an empty EXIF dictionary (`{}`); GPS flagged as removed in output and report; no files written during preview.
- Python 3.13.5, Pillow 13.0.0.

## Known gaps

- JPEG re-encoding is lossy: stripped JPEGs are visually identical but not byte-identical in pixel data.
- Single-frame images only (no animated GIF/multi-page TIFF handling).
- Stripping targets EXIF (including the GPS IFD) and Pillow-carried info chunks; other metadata containers (e.g. XMP packets) are not explicitly targeted.
- No linter/typechecker configured; project targets Python 3.9+.
