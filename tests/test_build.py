from build import slug_for_code


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


from build import generate_placeholder


class TestGeneratePlaceholder:
    def test_creates_file(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        assert dst.exists()

    def test_correct_dimensions(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        with Image.open(dst) as img:
            assert img.width == 600
            assert img.height == 400

    def test_webp_format(self, tmp_path):
        dst = tmp_path / "placeholder.webp"
        generate_placeholder(dst)
        with Image.open(dst) as img:
            assert img.format == "WEBP"

from pathlib import Path
from PIL import Image
import pytest

from build import resize_image, WEB_MAX_SIZE


@pytest.fixture
def sample_png(tmp_path):
    """Create a 1920x1080 red PNG for tests."""
    src = tmp_path / "sample.png"
    img = Image.new("RGB", (1920, 1080), color=(255, 0, 0))
    img.save(src, "PNG")
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
        # Source is 1920x1080 (16:9). At max 600x400 (3:2), we should
        # hit the width limit first and get 600x337.
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        with Image.open(dst) as out:
            assert out.width == 600
            assert 335 <= out.height <= 340  # 337 ± rounding

    def test_output_is_webp_format(self, sample_png, tmp_path):
        dst = tmp_path / "sample.webp"
        resize_image(sample_png, dst)
        with Image.open(dst) as out:
            assert out.format == "WEBP"


from build import build_manifest, WEB_URL_BASE


class TestBuildManifest:
    def test_empty_directory(self, tmp_path):
        assert build_manifest(tmp_path) == []

    def test_single_file(self, tmp_path):
        (tmp_path / "cah.webp").write_bytes(b"fake")
        result = build_manifest(tmp_path)
        assert result == [
            {"code": "CAH", "url": f"{WEB_URL_BASE}cah.webp"},
        ]

    def test_multiple_files_sorted_by_code(self, tmp_path):
        (tmp_path / "rnh.webp").write_bytes(b"fake")
        (tmp_path / "cah.webp").write_bytes(b"fake")
        (tmp_path / "bz4.webp").write_bytes(b"fake")
        result = build_manifest(tmp_path)
        codes = [entry["code"] for entry in result]
        assert codes == ["BZ4", "CAH", "RNH"]

    def test_ignores_non_webp_files(self, tmp_path):
        (tmp_path / "cah.webp").write_bytes(b"fake")
        (tmp_path / "readme.txt").write_bytes(b"ignore me")
        (tmp_path / "source.png").write_bytes(b"ignore me")
        result = build_manifest(tmp_path)
        assert len(result) == 1
        assert result[0]["code"] == "CAH"

    def test_handles_slash_in_code(self, tmp_path):
        # l-c.webp is the slug for Series code "L/C"
        (tmp_path / "l-c.webp").write_bytes(b"fake")
        result = build_manifest(tmp_path)
        # Note: manifest stores the slug, not the original code — the
        # reverse-mapping is applied by validate.py when comparing to
        # series_codes.csv.
        assert result == [
            {"code": "L-C", "url": f"{WEB_URL_BASE}l-c.webp"},
        ]
