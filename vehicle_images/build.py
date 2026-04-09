"""Build pipeline for the vehicle_images repo.

Regenerates images-web/ derivatives, manifest.json, placeholder.webp, and
index.html from the canonical PNG sources in images/.
"""


def slug_for_code(code: str) -> str:
    """Convert a Series code to its URL-safe filename stem.

    Lowercases and replaces `/` with `-` (the only non-URL-safe character
    that appears in d_VehicleSpecs[Series], specifically `L/C` for Land
    Cruiser 70).
    """
    return code.lower().replace("/", "-")

from pathlib import Path
from PIL import Image

WEB_MAX_SIZE = (600, 400)
WEB_QUALITY = 85


def resize_image(src: Path, dst: Path) -> None:
    """Resize an image to fit within WEB_MAX_SIZE and save as WebP.

    Preserves aspect ratio. The output is always WebP at quality 85.
    Creates parent directories as needed.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        img.thumbnail(WEB_MAX_SIZE, Image.Resampling.LANCZOS)
        # Convert to RGB if needed (WebP supports RGBA too, but RGB is smaller
        # and these are product photos without transparency requirements).
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.save(dst, "WEBP", quality=WEB_QUALITY)
