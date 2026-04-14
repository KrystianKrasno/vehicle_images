"""Build pipeline for vehicle_images.

Regenerates images-web/ derivatives, manifest.json, placeholder.webp,
and index.html from the canonical PNG sources in images/.
"""

import csv
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WEB_MAX_SIZE = (600, 400)
WEB_QUALITY = 95
WEB_URL_BASE = (
    "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"
)

DUPE_PAIRS = [
    # Tacoma/Tundra 4X2 and 4X4 share the same image
    ("cp2.webp", "cp4.webp"),
    ("tp2.webp", "tp4.webp"),
    # Family image sharing (source, target)
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def slug_for_code(code: str) -> str:
    """Convert a Series code to its URL-safe filename stem.

    Lowercases and replaces ``/`` with ``-`` (e.g. ``L/C`` becomes ``l-c``).
    """
    return code.lower().replace("/", "-")


def resize_image(src: Path, dst: Path) -> None:
    """Resize *src* to fit within WEB_MAX_SIZE and save as WebP at *dst*."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        img.thumbnail(WEB_MAX_SIZE, Image.Resampling.LANCZOS)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.save(dst, "WEBP", quality=WEB_QUALITY)


def build_manifest(images_web_dir: Path) -> list[dict]:
    """Return ``[{code, url}, ...]`` for every WebP in *images_web_dir*."""
    entries = []
    for path in sorted(images_web_dir.glob("*.webp")):
        entries.append({
            "code": path.stem.upper(),
            "url": WEB_URL_BASE + path.name,
        })
    return entries


def generate_placeholder(dst: Path) -> None:
    """Create a 600x400 gray placeholder WebP with centered 'No image' text."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", WEB_MAX_SIZE, color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    text = "No image"
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (WEB_MAX_SIZE[0] - (bbox[2] - bbox[0])) // 2
    y = (WEB_MAX_SIZE[1] - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), text, fill=(120, 120, 120), font=font)
    img.save(dst, "WEBP", quality=WEB_QUALITY)


def apply_dupe_pairs(images_web_dir: Path) -> None:
    """Copy images so related Series codes share a family image.

    If only one side of a pair exists, it is copied to the other.
    """
    for left_name, right_name in DUPE_PAIRS:
        left = images_web_dir / left_name
        right = images_web_dir / right_name
        if left.exists() and not right.exists():
            shutil.copy2(left, right)
        elif right.exists() and not left.exists():
            shutil.copy2(right, left)


def load_series_info(csv_path: Path) -> dict[str, dict]:
    """Load series_codes.csv into a dict keyed by Series code."""
    result: dict[str, dict] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = row["Series"].strip()
            family = row["Series Family"].strip()
            result[code] = {
                "description": family,
                "family": family,
                "active": True,
            }
    return result


def generate_gallery_html(
    manifest: list[dict], series_info: dict[str, dict]
) -> str:
    """Return an HTML gallery page grouped by Series Family."""
    by_family: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for entry in manifest:
        code = entry["code"]
        info = series_info.get(code, {})
        by_family[info.get("family", "Unknown")].append((
            code,
            info.get("description", code),
            entry["url"],
        ))

    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '    <meta charset="utf-8">',
        "    <title>Vehicle Images Gallery</title>",
        "    <style>",
        "        body { font-family: sans-serif; max-width: 1400px;"
        " margin: 0 auto; padding: 20px; }",
        "        h1 { border-bottom: 2px solid #333; padding-bottom: 8px; }",
        "        h2 { color: #555; margin-top: 32px; }",
        "        .grid { display: flex; flex-wrap: wrap; gap: 16px; }",
        "        figure { margin: 0; text-align: center; }",
        "        .grid img { max-width: 240px; height: auto;"
        " border: 1px solid #ccc; background: #f6f6f6; }",
        "        figcaption { font-size: 12px; color: #666; margin-top: 4px; }",
        "    </style>",
        "</head>",
        "<body>",
        "    <h1>Vehicle Images Gallery</h1>",
    ]
    for family in sorted(by_family):
        parts.append(f"    <h2>{family}</h2>")
        parts.append('    <div class="grid">')
        for code, desc, url in sorted(by_family[family], key=lambda t: t[1]):
            parts.append("        <figure>")
            parts.append(
                f'            <img src="{url}" alt="{desc}" title="{code}">'
            )
            parts.append(
                f"            <figcaption>{desc} <small>({code})</small>"
                "</figcaption>"
            )
            parts.append("        </figure>")
        parts.append("    </div>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


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

    if images_web_dir.exists():
        shutil.rmtree(images_web_dir)
    images_web_dir.mkdir(parents=True)

    source_files = sorted(images_dir.glob("*.png")) + sorted(
        images_dir.glob("*.jpg")
    )
    for src in source_files:
        resize_image(src, images_web_dir / f"{src.stem}.webp")

    apply_dupe_pairs(images_web_dir)
    generate_placeholder(placeholder_path)

    manifest = [
        e for e in build_manifest(images_web_dir) if e["code"] != "PLACEHOLDER"
    ]
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    if series_csv_path.exists():
        series_info = load_series_info(series_csv_path)
    else:
        print(
            f"WARN: {series_csv_path} missing; gallery will lack grouping",
            file=sys.stderr,
        )
        series_info = {}

    index_html_path.write_text(
        generate_gallery_html(manifest, series_info), encoding="utf-8"
    )

    print(f"Processed {len(source_files)} source images")
    print(f"Wrote {len(manifest)} manifest entries to {manifest_path.name}")
    print(f"Regenerated {index_html_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
