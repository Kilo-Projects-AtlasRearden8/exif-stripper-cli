#!/usr/bin/env python3
"""exif-stripper: strip EXIF and GPS metadata from photos locally.

A small, local-first CLI for beginner-friendly privacy tooling. Nothing is
uploaded, no account is needed, and every change is previewed before saving.

Credit: Asdale Dynamics, LLC (Indiana, formed Oct 2026).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}
GPS_IFD_TAG = 0x8825


def _tag_name(tag_id: int) -> str:
    from PIL.ExifTags import TAGS, GPSTAGS  # imported locally to keep startup light

    return TAGS.get(tag_id, str(tag_id))


def _serialize(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    return str(value)


def collect_metadata(path: str) -> dict[str, Any]:
    """Return a plain-English summary of the EXIF/GPS metadata in an image.

    The file is only read; nothing is modified.
    """
    from PIL.ExifTags import TAGS, GPSTAGS

    with Image.open(path) as img:
        exif = img.getexif()
        tags: dict[str, Any] = {}
        gps: dict[str, Any] = {}
        for tag_id in exif.keys():
            name = _tag_name(tag_id)
            if tag_id == GPS_IFD_TAG:
                for gps_id, gps_value in exif.get_ifd(GPS_IFD_TAG).items():
                    gps[GPSTAGS.get(gps_id, str(gps_id))] = _serialize(gps_value)
            else:
                tags[name] = _serialize(exif.get(tag_id))
        if gps:
            tags["GPSInfo"] = gps
        return tags


def _default_output(src: str) -> str:
    root, ext = os.path.splitext(src)
    return f"{root}_stripped{ext}"


def strip_image(src: str, dst: str | None = None, in_place: bool = False) -> dict[str, Any]:
    """Strip EXIF/GPS metadata from ``src`` and save a clean copy to ``dst``.

    Returns a report dict describing what was removed.
    """
    removed = collect_metadata(src)

    with Image.open(src) as img:
        fmt = img.format
        mode = img.mode
        size = img.size
        data = img.tobytes()

    working_mode = mode if mode in ("RGB", "RGBA", "L") else "RGB"
    clean = Image.new(working_mode, size)
    clean.frombytes(data, "raw")
    clean.info.clear()

    if in_place:
        out = src
    elif dst is not None:
        out = dst
    else:
        out = _default_output(src)

    save_kwargs: dict[str, Any] = {}
    if fmt == "JPEG":
        save_kwargs["quality"] = 95
        save_kwargs["exif"] = b""
    clean.save(out, format=fmt, **save_kwargs)

    return {
        "source": os.path.abspath(src),
        "output": os.path.abspath(out),
        "format": fmt,
        "removed_tags": removed,
        "gps_removed": bool(removed.get("GPSInfo")),
        "status": "stripped",
    }


def _list_images(path: str) -> list[str]:
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames.sort()
        for name in sorted(filenames):
            if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                found.append(os.path.join(dirpath, name))
    return found


def _resolve_output(args: argparse.Namespace, src: str, input_root: str | None) -> str | None:
    if args.in_place:
        return None
    if args.output is not None and (
        os.path.isdir(args.output) or _is_multi_input(args)
    ):
        rel = os.path.relpath(src, input_root) if input_root else os.path.basename(src)
        root, ext = os.path.splitext(rel)
        return os.path.join(args.output, f"{root}_stripped{ext}")
    if args.output is not None:
        return args.output
    return None


def _is_multi_input(args: argparse.Namespace) -> bool:
    return os.path.isdir(args.input) and bool(args.batch)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="exif-stripper",
        description="Strip EXIF and GPS metadata from photos locally. "
        "Nothing leaves your computer.",
    )
    parser.add_argument("input", help="Image file or directory to process")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show what metadata would be removed, without saving changes",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the original files instead of creating new ones",
    )
    parser.add_argument("--report", help="Export a JSON report to this path")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process every image inside a directory",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"error: not found: {args.input}", file=sys.stderr)
        return 1

    if os.path.isdir(args.input) and not args.batch:
        print(
            "error: input is a directory; pass --batch to process all images in it",
            file=sys.stderr,
        )
        return 2

    inputs = [args.input] if os.path.isfile(args.input) else _list_images(args.input)
    input_root = os.path.dirname(os.path.abspath(args.input)) if os.path.isfile(args.input) else args.input

    if not inputs:
        print("no image files found")
        return 0

    results: list[dict[str, Any]] = []
    ok = True
    for src in inputs:
        entry: dict[str, Any] = {"source": os.path.abspath(src)}
        try:
            if args.preview:
                meta = collect_metadata(src)
                entry.update(
                    {
                        "removed_tags": meta,
                        "gps_removed": bool(meta.get("GPSInfo")),
                        "status": "preview",
                    }
                )
                print(f"== {src}")
                if not meta:
                    print("   no EXIF/GPS metadata found")
                else:
                    print(f"   {len(meta)} metadata field(s) would be removed:")
                    for key, value in meta.items():
                        print(f"   - {key}: {value}")
            else:
                out = _resolve_output(args, src, input_root)
                if out is not None:
                    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
                result = strip_image(src, out, args.in_place)
                entry.update(result)
                extra = " (GPS removed)" if result["gps_removed"] else ""
                print(f"stripped: {src} -> {result['output']}{extra}")
        except Exception as exc:  # keep batch runs going; report per file
            ok = False
            entry.update({"status": "error", "error": str(exc)})
            print(f"error: {src}: {exc}", file=sys.stderr)
        results.append(entry)

    if args.report:
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "preview": args.preview,
            "total_files": len(inputs),
            "completed": sum(1 for r in results if r["status"] in ("stripped", "preview")),
            "errors": sum(1 for r in results if r["status"] == "error"),
            "files": results,
        }
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        print(f"report written to {args.report}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
