from pathlib import Path

import pytest
from PIL import Image

from build import (
    WEB_MAX_SIZE,
    WEB_URL_BASE,
    apply_dupe_pairs,
    build_manifest,
    generate_gallery_html,
    generate_placeholder,
    load_series_info,
    resize_image,
    slug_for_code,
)


class TestSlugForCode:
    def test_plain_uppercase_code(self):
        assert slug_for_code("CAH") == "cah"

    def test_numeric_suffix_code(self):
        assert slug_for_code("BZ4") == "bz4"

    def test_code_with_forward_slash(self):
        assert slug_for_code("L/C") == "l-c"

    def test_already_lowercase(self):
        assert slug_for_code("cah") == "cah"

    def test_empty_string(self):
        assert slug_for_code("") == ""


@pytest.fixture
def sample_png(tmp_path):
    """Create a 1920x1080 red PNG for tests."""
    src = tmp_path / "sample.png"
    Image.new("RGB", (1920, 1080), color=(255, 0, 0)).save(src, "PNG")
    return src


class TestResizeImage:
    def test_produces_webp_output(self, sample_png, tmp_path):
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        assert dst.exists()
        assert dst.stat().st_size > 0

    def test_fits_within_max_dimensions(self, sample_png, tmp_path):
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        with Image.open(dst) as out:
            assert out.width <= WEB_MAX_SIZE[0]
            assert out.height <= WEB_MAX_SIZE[1]

    def test_preserves_aspect_ratio(self, sample_png, tmp_path):
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        with Image.open(dst) as out:
            assert out.width == 600
            assert 335 <= out.height <= 340

    def test_output_is_webp_format(self, sample_png, tmp_path):
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        with Image.open(dst) as out:
            assert out.format == "WEBP"


class TestBuildManifest:
    def test_empty_directory(self, tmp_path):
        assert build_manifest(tmp_path) == []

    def test_single_file(self, tmp_path):
        (tmp_path / "cah.webp").write_bytes(b"fake")
        result = build_manifest(tmp_path)
        assert result == [{"code": "CAH", "url": f"{WEB_URL_BASE}cah.webp"}]

    def test_multiple_files_sorted_by_code(self, tmp_path):
        for name in ("rnh.webp", "cah.webp", "bz4.webp"):
            (tmp_path / name).write_bytes(b"fake")
        codes = [e["code"] for e in build_manifest(tmp_path)]
        assert codes == ["BZ4", "CAH", "RNH"]

    def test_ignores_non_webp_files(self, tmp_path):
        (tmp_path / "cah.webp").write_bytes(b"fake")
        (tmp_path / "readme.txt").write_bytes(b"ignore me")
        (tmp_path / "source.png").write_bytes(b"ignore me")
        assert len(build_manifest(tmp_path)) == 1

    def test_handles_slash_in_code(self, tmp_path):
        (tmp_path / "l-c.webp").write_bytes(b"fake")
        result = build_manifest(tmp_path)
        assert result == [{"code": "L-C", "url": f"{WEB_URL_BASE}l-c.webp"}]


class TestGeneratePlaceholder:
    def test_creates_file(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        assert dst.exists()

    def test_correct_dimensions(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        with Image.open(dst) as img:
            assert (img.width, img.height) == (600, 400)

    def test_webp_format(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        with Image.open(dst) as img:
            assert img.format == "WEBP"


class TestApplyDupePairs:
    def test_copies_left_to_right(self, tmp_path):
        (tmp_path / "cp4.webp").write_bytes(b"tacoma")
        apply_dupe_pairs(tmp_path)
        assert (tmp_path / "cp2.webp").read_bytes() == b"tacoma"

    def test_copies_right_to_left(self, tmp_path):
        (tmp_path / "cp2.webp").write_bytes(b"tacoma")
        apply_dupe_pairs(tmp_path)
        assert (tmp_path / "cp4.webp").read_bytes() == b"tacoma"

    def test_noop_when_both_exist(self, tmp_path):
        (tmp_path / "cp2.webp").write_bytes(b"original-cp2")
        (tmp_path / "cp4.webp").write_bytes(b"original-cp4")
        apply_dupe_pairs(tmp_path)
        assert (tmp_path / "cp2.webp").read_bytes() == b"original-cp2"
        assert (tmp_path / "cp4.webp").read_bytes() == b"original-cp4"

    def test_noop_when_neither_exists(self, tmp_path):
        apply_dupe_pairs(tmp_path)
        assert not (tmp_path / "cp2.webp").exists()


class TestGenerateGalleryHtml:
    def test_includes_all_images(self):
        manifest = [
            {"code": "CAH", "url": "https://example.com/cah.webp"},
            {"code": "CAM", "url": "https://example.com/cam.webp"},
        ]
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry"},
            "CAM": {"description": "Camry", "family": "Camry"},
        }
        html = generate_gallery_html(manifest, series_info)
        assert "cah.webp" in html
        assert "cam.webp" in html

    def test_groups_by_family(self):
        manifest = [
            {"code": "CAH", "url": "https://example.com/cah.webp"},
            {"code": "RNH", "url": "https://example.com/rnh.webp"},
        ]
        series_info = {
            "CAH": {"description": "Camry HV", "family": "Camry"},
            "RNH": {"description": "4Runner HV", "family": "4Runner"},
        }
        html = generate_gallery_html(manifest, series_info)
        assert html.index("4Runner") < html.index("Camry")

    def test_handles_unknown_code(self):
        manifest = [{"code": "XXX", "url": "https://example.com/xxx.webp"}]
        html = generate_gallery_html(manifest, {})
        assert "xxx.webp" in html
        assert "XXX" in html

    def test_empty_manifest(self):
        html = generate_gallery_html([], {})
        assert "<!DOCTYPE html>" in html


class TestLoadSeriesInfo:
    def test_parses_csv(self, tmp_path):
        csv_path = tmp_path / "series.csv"
        csv_path.write_text("Series Family,Series\nCamry,CAH\n4Runner,RNH\n")
        info = load_series_info(csv_path)
        assert info["CAH"] == {
            "description": "Camry",
            "family": "Camry",
            "active": True,
        }
        assert info["RNH"]["family"] == "4Runner"

    def test_all_entries_are_active(self, tmp_path):
        csv_path = tmp_path / "series.csv"
        csv_path.write_text("Series Family,Series\nCorolla,COR\n")
        assert load_series_info(csv_path)["COR"]["active"] is True

    def test_handles_slash_code(self, tmp_path):
        csv_path = tmp_path / "series.csv"
        csv_path.write_text("Series Family,Series\nLand Cruiser,L/C\n")
        assert "L/C" in load_series_info(csv_path)
