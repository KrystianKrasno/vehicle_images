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
