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


WEB_URL_BASE = "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"


def build_manifest(images_web_dir: Path) -> list[dict]:
    """Scan images_web_dir for WebP files and build a manifest list.

    Returns a list of dicts sorted by code, each containing:
      - code: uppercase stem of the filename (e.g. "CAH")
      - url:  full public GitHub Pages URL
    """
    entries = []
    for path in sorted(images_web_dir.glob("*.webp")):
        code = path.stem.upper()
        entries.append({
            "code": code,
            "url": WEB_URL_BASE + path.name,
        })
    return entries


from PIL import ImageDraw, ImageFont


def generate_placeholder(dst: Path) -> None:
    """Create a neutral 600x400 gray placeholder WebP with 'No image' text."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", WEB_MAX_SIZE, color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    text = "No image"
    # Use default font — Pillow ships with a usable bitmap font that works
    # without extra asset downloads. Looks plain but that's fine for a fallback.
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        font = ImageFont.load_default()
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WEB_MAX_SIZE[0] - text_width) // 2
    y = (WEB_MAX_SIZE[1] - text_height) // 2
    draw.text((x, y), text, fill=(120, 120, 120), font=font)
    img.save(dst, "WEBP", quality=WEB_QUALITY)


import shutil

DUPE_PAIRS = [
    # Tacoma/Tundra 4X2 ↔ 4X4
    ("cp2.webp", "cp4.webp"),
    ("tp2.webp", "tp4.webp"),
    # Family image sharing: source → target
    ("bz4.webp", "bzd.webp"),
    ("cp4.webp", "cph.webp"),
    ("es.webp", "ese.webp"),
    ("es.webp", "esh.webp"),
    ("ghi.webp", "ghh.webp"),
    ("hig.webp", "hih.webp"),
    ("lch.webp", "lcc.webp"),
    ("ls.webp", "lsh.webp"),
    ("nx.webp", "nxh.webp"),
    ("prd.webp", "l-c.webp"),
    ("prd.webp", "tz.webp"),
    ("rav.webp", "rah.webp"),
    ("rc.webp", "rcf.webp"),
    ("tp4.webp", "tph.webp"),
    ("tx.webp", "txh.webp"),
    ("ux.webp", "uxh.webp"),
]


def apply_dupe_pairs(images_web_dir: Path) -> None:
    """Copy images so that related Series codes share a family image.

    If only one of a pair exists, copies it to the missing sibling. If both
    exist, no-op. If neither exists, no-op.
    """
    for left_name, right_name in DUPE_PAIRS:
        left = images_web_dir / left_name
        right = images_web_dir / right_name
        if left.exists() and not right.exists():
            shutil.copy2(left, right)
        elif right.exists() and not left.exists():
            shutil.copy2(right, left)
from collections import defaultdict


def generate_gallery_html(manifest: list[dict], series_info: dict[str, dict]) -> str:
    """Generate an index.html string grouped by Series Family.

    Args:
        manifest: list of {code, url} dicts from build_manifest().
        series_info: dict mapping code -> {description, family}.

    Returns an HTML document as a string. Used for local sanity-checking
    the rendered gallery; not consumed by Power BI.
    """
    # Group manifest entries by family
    by_family: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for entry in manifest:
        code = entry["code"]
        url = entry["url"]
        info = series_info.get(code, {})
        family = info.get("family", "Unknown")
        description = info.get("description", code)
        by_family[family].append((code, description, url))

    # Sort families alphabetically
    families = sorted(by_family.keys())

    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '    <meta charset="utf-8">',
        "    <title>Vehicle Images Gallery</title>",
        "    <style>",
        "        body { font-family: sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; }",
        "        h1 { border-bottom: 2px solid #333; padding-bottom: 8px; }",
        "        h2 { color: #555; margin-top: 32px; }",
        "        .group { display: flex; flex-wrap: wrap; gap: 16px; }",
        "        figure { margin: 0; text-align: center; }",
        "        .group img { max-width: 240px; height: auto; border: 1px solid #ccc; background: #f6f6f6; }",
        "        figcaption { font-size: 12px; color: #666; margin-top: 4px; }",
        "    </style>",
        "</head>",
        "<body>",
        "    <h1>Vehicle Images Gallery</h1>",
        "    <p>Sanity-check gallery generated by build.py. Not consumed by Power BI.</p>",
    ]
    for family in families:
        parts.append(f"    <h2>{family}</h2>")
        parts.append('    <div class="group">')
        for code, description, url in sorted(by_family[family], key=lambda t: t[1]):
            parts.append("        <figure>")
            parts.append(f'            <img src="{url}" alt="{description}" title="{code}">')
            parts.append(f"            <figcaption>{description} <small>({code})</small></figcaption>")
            parts.append("        </figure>")
        parts.append("    </div>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


import csv
import json
import sys


def load_series_info(csv_path: Path) -> dict[str, dict]:
    """Load series_codes.csv into a dict keyed by Series code.

    Expects columns: Series Family, Series.  All entries are treated as active.
    """
    result: dict[str, dict] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["Series"].strip()
            family = row["Series Family"].strip()
            result[code] = {
                "description": family,
                "family": family,
                "active": True,
            }
    return result


def main() -> int:
    """Regenerate all derived artifacts from vehicle_images/images/."""
    root = Path(__file__).parent
    images_dir = root / "images"
    images_web_dir = root / "images-web"
    manifest_path = root / "manifest.json"
    placeholder_path = images_web_dir / "placeholder.webp"
    series_csv_path = root / "series_codes.csv"
    index_html_path = root / "index.html"

    if not images_dir.exists():
        print(f"ERROR: {images_dir} does not exist", file=sys.stderr)
        return 1

    # Clear and recreate images-web/
    if images_web_dir.exists():
        shutil.rmtree(images_web_dir)
    images_web_dir.mkdir(parents=True)

    # Resize every source image
    source_files = sorted(images_dir.glob("*.png")) + sorted(images_dir.glob("*.jpg"))
    resized_count = 0
    for src in source_files:
        dst = images_web_dir / f"{src.stem}.webp"
        resize_image(src, dst)
        resized_count += 1

    # Apply family image sharing
    apply_dupe_pairs(images_web_dir)

    # Generate placeholder
    generate_placeholder(placeholder_path)

    # Build manifest (excluding the placeholder itself)
    manifest = [
        entry for entry in build_manifest(images_web_dir)
        if entry["code"] != "PLACEHOLDER"
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Generate gallery HTML
    if series_csv_path.exists():
        series_info = load_series_info(series_csv_path)
    else:
        print(f"WARN: {series_csv_path} missing; gallery will lack family grouping",
              file=sys.stderr)
        series_info = {}
    html = generate_gallery_html(manifest, series_info)
    index_html_path.write_text(html, encoding="utf-8")

    # Summary
    print(f"Processed {resized_count} source images")
    print(f"Wrote {len(manifest)} manifest entries to {manifest_path.name}")
    print(f"Regenerated {index_html_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
