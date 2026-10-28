"""Tests for exif_stripper: metadata removal, preview, batch, and reports."""

import json
import os

import pytest
from PIL import Image

import exif_stripper


def _make_image(path, with_gps=False, make="TestMake", model="TestModel"):
    img = Image.new("RGB", (100, 100), color=(11, 22, 33))
    exif = Image.Exif()
    exif[0x010F] = make
    exif[0x0110] = model
    if with_gps:
        gps = exif.get_ifd(exif_stripper.GPS_IFD_TAG)
        gps[0x0001] = "N"
        gps[0x0002] = (37.5, 46.0, 29.25)
        gps[0x0003] = "W"
        gps[0x0004] = 123.5
    img.save(path, exif=exif)


def test_collect_metadata_reads_exif_and_gps(tmp_path):
    p = tmp_path / "a.jpg"
    _make_image(p, with_gps=True)
    meta = exif_stripper.collect_metadata(str(p))
    assert meta["Make"] == "TestMake"
    assert meta["Model"] == "TestModel"
    assert "GPSInfo" in meta
    assert meta["GPSInfo"]["GPSLatitudeRef"] == "N"


def test_collect_metadata_empty_for_clean_file(tmp_path):
    p = tmp_path / "clean.jpg"
    Image.new("RGB", (10, 10)).save(p)
    assert exif_stripper.collect_metadata(str(p)) == {}


def test_strip_removes_exif_and_gps(tmp_path):
    src = tmp_path / "src.jpg"
    dst = tmp_path / "dst.jpg"
    _make_image(src, with_gps=True)
    entry = exif_stripper.strip_image(str(src), str(dst))

    assert entry["status"] == "stripped"
    assert entry["gps_removed"] is True
    assert entry["removed_tags"]["Make"] == "TestMake"

    with Image.open(dst) as img:
        assert not img.getexif()
        pixel = img.getpixel((0, 0))
        assert all(abs(a - b) <= 6 for a, b in zip(pixel, (11, 22, 33)))

    # the original is untouched when not in-place
    with Image.open(src) as img:
        assert img.getexif()


def test_strip_in_place_overwrites_original(tmp_path):
    src = tmp_path / "inplace.jpg"
    _make_image(src)
    exif_stripper.strip_image(str(src), in_place=True)
    with Image.open(src) as img:
        assert not img.getexif()


def test_strip_default_output_named_stripped(tmp_path):
    src = tmp_path / "photo.jpg"
    _make_image(src)
    exif_stripper.strip_image(str(src))
    assert (tmp_path / "photo_stripped.jpg").exists()
    with Image.open(tmp_path / "photo_stripped.jpg") as img:
        assert not img.getexif()


def test_preview_writes_no_files(tmp_path, capsys):
    src = tmp_path / "preview.jpg"
    _make_image(src, with_gps=True)
    before = set(os.listdir(tmp_path))
    code = exif_stripper.main(["--preview", str(src)])
    assert code == 0
    assert set(os.listdir(tmp_path)) == before
    output = capsys.readouterr().out
    assert "TestMake" in output
    assert "GPSInfo" in output
    assert "would be removed" in output


def test_main_single_file_strips(tmp_path):
    src = tmp_path / "one.jpg"
    dst = tmp_path / "one_out.jpg"
    _make_image(src)
    code = exif_stripper.main(["-o", str(dst), str(src)])
    assert code == 0
    assert dst.exists()
    with Image.open(dst) as img:
        assert not img.getexif()


def test_batch_directory(tmp_path):
    os.makedirs(tmp_path / "sub")
    _make_image(tmp_path / "a.jpg")
    _make_image(tmp_path / "sub" / "b.jpg")
    outdir = tmp_path / "out"
    code = exif_stripper.main(["--batch", "--output", str(outdir), str(tmp_path)])
    assert code == 0
    assert (outdir / "a_stripped.jpg").exists()
    assert (outdir / "sub" / "b_stripped.jpg").exists()
    with Image.open(outdir / "a_stripped.jpg") as img:
        assert not img.getexif()


def test_batch_in_place(tmp_path):
    _make_image(tmp_path / "a.jpg")
    _make_image(tmp_path / "b.jpg")
    code = exif_stripper.main(["--batch", "--in-place", str(tmp_path)])
    assert code == 0
    for name in ("a.jpg", "b.jpg"):
        with Image.open(tmp_path / name) as img:
            assert not img.getexif()


def test_report_exported(tmp_path):
    src = tmp_path / "report.jpg"
    _make_image(src, with_gps=True)
    report_path = tmp_path / "report.json"
    code = exif_stripper.main(["--output", str(tmp_path / "out.jpg"), "--report", str(report_path), str(src)])
    assert code == 0
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["total_files"] == 1
    assert data["completed"] == 1
    assert data["errors"] == 0
    assert data["files"][0]["status"] == "stripped"
    assert data["files"][0]["gps_removed"] is True


def test_directory_without_batch_errors(tmp_path):
    _make_image(tmp_path / "a.jpg")
    code = exif_stripper.main([str(tmp_path)])
    assert code == 2


def test_missing_file_errors(tmp_path):
    code = exif_stripper.main([str(tmp_path / "nope.jpg")])
    assert code == 1
