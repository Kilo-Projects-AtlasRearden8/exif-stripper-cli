# exif-stripper

A tiny, local-first Python CLI that strips EXIF and GPS metadata from photos before you share them. You see exactly what will be removed (preview), then save clean copies. Nothing is uploaded, no account is needed, and nothing ever leaves your computer.

Built with care by **Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI education, books, and practical tools you can actually use. See [dylanasdale.github.io](https://dylanasdale.github.io).

## Why this exists

Photos carry hidden metadata: where and when they were taken, what camera took them, sometimes GPS coordinates. Stripping that metadata before posting or sending a photo is a simple privacy habit. This tool makes it explicit: preview first, then strip.

## Features

- Strip EXIF and GPS metadata from JPEG, PNG, TIFF, WebP, and BMP images
- Preview exactly which metadata fields will be removed, before anything is saved
- Process one file, many files, or a whole folder (`--batch`)
- Save stripped copies alongside the originals, to a folder of your choice, or overwrite in place (`--in-place`)
- Export a JSON report of everything that was removed (`--report`)
- Runs entirely offline — no cloud, no accounts, no network access at all

## Install

```bash
pip install Pillow
```

Or install the package itself (adds an `exif-stripper` command):

```bash
pip install -e .
```

You can also run it directly:

```bash
python exif_stripper.py ...
```

## Usage

Preview what would be removed (nothing is saved):

```bash
python exif_stripper.py --preview vacation.jpg
```

Strip metadata and save a new file (`vacation_stripped.jpg`):

```bash
python exif_stripper.py vacation.jpg
```

Choose the output:

```bash
python exif_stripper.py -o clean/vacation.jpg vacation.jpg
```

Overwrite the originals:

```bash
python exif_stripper.py --in-place vacation.jpg
```

Process every image in a folder:

```bash
python exif_stripper.py --batch --output cleaned/ photos/
```

Export a JSON report:

```bash
python exif_stripper.py --batch --output cleaned/ --report report.json photos/
```

## Tests

```bash
python -m pytest tests/
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About Asdale Dynamics, LLC

Dylan Asdale is a registered nurse turned AI author and founder of Asdale Dynamics, LLC. The LLC publishes beginner-friendly AI education — plain English, step by step, never condescending — including *The Massive AI Manual* and the hub site dylanasdale.github.io. This tool is part of that mission: practical, local-first software anyone can understand and use.
