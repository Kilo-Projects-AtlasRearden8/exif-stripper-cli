# exif-stripper

A tiny, local-first Python CLI that strips EXIF and GPS metadata from your photos before you share them. You see exactly what will be removed (preview), then save clean copies. Nothing is uploaded, no account is needed, and nothing ever leaves your computer.

Built with care by **Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI education, books, and practical tools you can actually use. See [dylanasdale.github.io](https://dylanasdale.github.io).

## Why this exists

Photos carry hidden metadata: when and where they were taken, what camera took them, sometimes even GPS coordinates. Stripping that metadata before posting or sending a photo is a simple privacy habit. This tool makes it explicit — preview first, then strip — so nothing surprises you.

## Features

- Strip EXIF and GPS metadata from JPEG, PNG, TIFF, WebP, and BMP images
- Preview exactly which metadata fields will be removed, before anything is saved
- Process one file, many files, or a whole folder (`--batch`)
- Save stripped copies alongside originals, to a folder of your choice, or overwrite in place (`--in-place`)
- Export a JSON report of everything removed (`--report`)
- Runs entirely offline — no cloud, no accounts, no network access at all

## Install

You need Python 3.9+ and [Pillow](https://pypi.org/project/Pillow/):

```bash
pip install Pillow
```

You can then run the tool directly:

```bash
python exif_stripper.py --preview vacation.jpg
```

Or install it as a command on your system so you can type `exif-stripper` from anywhere:

```bash
pip install -e .
```

## Usage

Preview what would be removed (nothing is saved):

```bash
python exif_stripper.py --preview vacation.jpg
```

Sample output:

```
== vacation.jpg
   3 metadata field(s) would be removed:
   - Make: Canon
   - Model: EOS R5
   - GPSInfo: {'GPSLatitudeRef': 'N', 'GPSLatitude': ['37.5', '46.0', '29.25'], 'GPSLongitudeRef': 'W', 'GPSLongitude': '123.5'}
   (preview mode: no files were modified)
```

Strip metadata and save a new file (`vacation_stripped.jpg`) next to the original:

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

That writes `cleaned/photo_stripped.jpg` for every `photo.jpg` found inside `photos/` (including subfolders).

Export a JSON report:

```bash
python exif_stripper.py --batch --output cleaned/ --report report.json photos/
```

The report lists each file, what tags were removed, whether GPS was present, and whether each file succeeded.

## Tests

```bash
python -m pytest tests/
```

There are 14 tests covering metadata removal, preview-as-dry-run, batch folders, in-place mode, PNG handling, JSON reports, and error cases.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About Asdale Dynamics, LLC

Dylan Asdale is a registered nurse turned AI author and founder of Asdale Dynamics, LLC. The LLC publishes beginner-friendly AI education — plain English, step by step, never condescending — including *The Massive AI Manual* and the hub site dylanasdale.github.io. This tool is part of that mission: practical, local-first software anyone can understand and use.
