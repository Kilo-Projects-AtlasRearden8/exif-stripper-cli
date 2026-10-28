# STATUS

## What was built

`exif-stripper`: a local-first Python CLI that strips EXIF and GPS metadata from photos. It previews exactly which metadata fields will be removed before anything is saved, supports single-file and batch (`--batch`) processing, writes stripped copies next to originals or to a chosen output directory (or in place with `--in-place`), and can export a JSON report (`--report`). Everything runs offline — no cloud, no accounts, no network.

Files:
- `exif_stripper.py` — the CLI (Pillow only)
- `tests/test_exif_stripper.py` — metadata-removal, preview, batch, in-place, and report tests
- `README.md` — plain-English usage guide crediting Asdale Dynamics, LLC
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `pyproject.toml` — installable package with `exif-stripper` console script

## How to run

```bash
python3 -m pip install Pillow            # or: pip install -e .
python3 exif_stripper.py --preview photo.jpg
python3 exif_stripper.py photo.jpg
python3 exif_stripper.py --batch --output cleaned/ --report report.json photos/
python3 -m pytest tests/
```

## Verification results

- `python3 -m pytest tests/`: 12 passed, covering EXIF/GPS collection, stripping, pixel preservation (within JPEG lossy tolerance), preview-without-writing, batch directory processing, in-place mode, report export, and error cases.
- Manual end-to-end: preview correctly lists Make/Model/GPSInfo fields; stripped output has an empty EXIF dictionary (`{}`); no files written during preview.
- Python 3.13.5, Pillow 13.0.0.

## Known gaps

- JPEG re-encoding is lossy: stripped JPEGs are visually identical but not byte-identical in pixel data.
- Single-frame images only (no animated GIF/multi-page TIFF handling).
- Stripping targets EXIF (including GPS IFD) and Pillow-carried info chunks; other metadata formats (e.g. XMP packets) are not explicitly targeted.
- No `my`py/ruff configured; project targets Python 3.9+.
