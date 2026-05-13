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
from rembg import remove as remove_bg

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WEB_MAX_SIZE = (600, 400)
WEB_QUALITY = 95
REMBG_MAX_SIZE = (1200, 800)  # Downsample before background removal to save RAM
REMBG_OPTS = {
    "alpha_matting": False,
}

# Normalization: vehicle should fill 75% of canvas, centered at 55% from top
NORM_FILL = 0.75  # Vehicle fits within 75% of both canvas width and height
NORM_VERTICAL_CENTER = 0.55  # Place vehicle center at 55% from top
NORM_MAX_UPSCALE = 1.10  # Never upscale more than 10%
NORM_BBOX_TRIM = 2  # Trim px from alpha bbox edges to remove rembg halo
NORM_FAIL_THRESHOLD = 0.85  # Fill > 85% = likely rembg failure
WEB_URL_BASE = (
    "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"
)

DUPE_PAIRS = [
    # Family image sharing (source, target)
    ("ghi.webp", "ghh.webp"),
    ("hig.webp", "hih.webp"),
    ("lch.webp", "lcc.webp"),
    ("ls.webp", "lsh.webp"),
    ("nx.webp", "nxh.webp"),
    ("prd.webp", "l-c.webp"),
    ("prd.webp", "tz.webp"),
    ("rav.webp", "rah.webp"),
    ("rc.webp", "rcf.webp"),
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


def _needs_bg_removal(img: Image.Image) -> bool:
    """Return True if the image has no meaningful transparency."""
    if img.mode != "RGBA":
        return True
    alpha = img.getchannel("A")
    # If less than 1% of pixels are transparent, it needs removal
    transparent = alpha.histogram()[0]
    return transparent / (img.width * img.height) < 0.01


def normalize_on_canvas(img: Image.Image) -> Image.Image:
    """Crop to vehicle bbox, scale to fill NORM_FILL of canvas, center at NORM_VERTICAL_CENTER.

    Returns a fixed WEB_MAX_SIZE RGBA image. If rembg likely failed (fill > threshold),
    returns the image as-is with a warning printed.
    """
    canvas_w, canvas_h = WEB_MAX_SIZE

    if img.mode != "RGBA":
        # No alpha channel — can't normalize, return as-is on canvas
        canvas = Image.new("RGBA", WEB_MAX_SIZE, (0, 0, 0, 0))
        img.thumbnail(WEB_MAX_SIZE, Image.Resampling.LANCZOS)
        paste_x = (canvas_w - img.width) // 2
        paste_y = (canvas_h - img.height) // 2
        canvas.paste(img, (paste_x, paste_y))
        return canvas

    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        # Fully transparent — return empty canvas
        return Image.new("RGBA", WEB_MAX_SIZE, (0, 0, 0, 0))

    # Check for rembg failure (vehicle fills almost the entire image)
    veh_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    img_area = img.width * img.height
    if veh_area / img_area > NORM_FAIL_THRESHOLD:
        print(f"  WARN: rembg may have failed (fill={veh_area / img_area:.0%}), passing through")
        canvas = Image.new("RGBA", WEB_MAX_SIZE, (0, 0, 0, 0))
        img.thumbnail(WEB_MAX_SIZE, Image.Resampling.LANCZOS)
        paste_x = (canvas_w - img.width) // 2
        paste_y = (canvas_h - img.height) // 2
        canvas.paste(img, (paste_x, paste_y), img)
        return canvas

    # Trim halo from bbox edges
    x0 = min(bbox[0] + NORM_BBOX_TRIM, bbox[2])
    y0 = min(bbox[1] + NORM_BBOX_TRIM, bbox[3])
    x1 = max(bbox[2] - NORM_BBOX_TRIM, x0)
    y1 = max(bbox[3] - NORM_BBOX_TRIM, y0)

    # Crop to vehicle
    vehicle = img.crop((x0, y0, x1, y1))
    vw, vh = vehicle.size

    # Target zone: 75% of canvas
    target_w = canvas_w * NORM_FILL
    target_h = canvas_h * NORM_FILL

    # Scale factor: fit within target zone, cap upscaling
    scale = min(target_w / vw, target_h / vh)
    scale = min(scale, NORM_MAX_UPSCALE)  # Cap upscale

    new_w = round(vw * scale)
    new_h = round(vh * scale)
    vehicle = vehicle.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Place on canvas: horizontally centered, vertically at 55% from top
    canvas = Image.new("RGBA", WEB_MAX_SIZE, (0, 0, 0, 0))
    paste_x = (canvas_w - new_w) // 2
    paste_y = round(canvas_h * NORM_VERTICAL_CENTER - new_h / 2)
    # Clamp to canvas bounds
    paste_y = max(0, min(paste_y, canvas_h - new_h))
    canvas.paste(vehicle, (paste_x, paste_y), vehicle)
    return canvas


def resize_image(src: Path, dst: Path) -> None:
    """Remove background if needed, normalize onto fixed canvas, save as WebP."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        if _needs_bg_removal(img):
            img.thumbnail(REMBG_MAX_SIZE, Image.Resampling.LANCZOS)
            img = remove_bg(img, **REMBG_OPTS)  # type: ignore[assignment]
        img = normalize_on_canvas(img)
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


def generate_qa_report(images_dir: Path, qa_dir: Path, filter_codes: list[str] | None = None) -> int:
    """Generate a side-by-side QA report without modifying production output.

    If *filter_codes* is provided, only process images whose stem matches.
    Returns the number of images processed.
    """
    if qa_dir.exists():
        shutil.rmtree(qa_dir)
    qa_dir.mkdir(parents=True)

    source_files = sorted(images_dir.glob("*.png")) + sorted(
        images_dir.glob("*.jpg")
    )
    if filter_codes:
        allowed = {c.lower() for c in filter_codes}
        source_files = [f for f in source_files if f.stem.lower() in allowed]
    entries = []
    for src in source_files:
        stem = src.stem.lower()
        before_path = qa_dir / f"{stem}_before.webp"
        after_path = qa_dir / f"{stem}_after.webp"

        with Image.open(src) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            # Save "before" thumbnail (no background foval)
            before = img.copy()
            before.thumbnail(WEB_MAX_SIZE, Image.Resampling.LANCZOS)
            if before.mode not in ("RGB", "RGBA"):
                before = before.convert("RGB")
            before.save(before_path, "WEBP", quality=WEB_QUALITY)

            # Save "after" (bg removal + normalization)
            if _needs_bg_removal(img):
                img_small = img.copy()
                img_small.thumbnail(REMBG_MAX_SIZE, Image.Resampling.LANCZOS)
                removed = remove_bg(img_small, **REMBG_OPTS)  # type: ignore[assignment]
                normalized = normalize_on_canvas(removed)
                normalized.save(after_path, "WEBP", quality=WEB_QUALITY)
                entries.append((stem, True))
            else:
                # Already has transparency — normalize onto canvas
                normalized = normalize_on_canvas(img)
                normalized.save(after_path, "WEBP", quality=WEB_QUALITY)
                entries.append((stem, False))

    # Generate HTML report
    rows = []
    for stem, processed in entries:
        status = "Removed" if processed else "Skipped (already transparent)"
        rows.append(
            f"<tr>"
            f"<td><strong>{stem.upper()}</strong><br><small>{status}</small></td>"
            f"<td><img src='{stem}_before.webp'></td>"
            f"<td><img src='{stem}_after.webp'></td>"
            f"</tr>"
        )

    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>QA Review - Background Removal</title>"
        "<style>"
        "body{font-family:sans-serif;max-width:1400px;margin:0 auto;padding:20px}"
        "table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #ccc;padding:8px;text-align:center}"
        "img{max-width:300px;height:auto;background:repeating-conic-gradient("
        "#ddd 0% 25%,#fff 0% 50%) 50%/20px 20px}"
        "</style></head><body>"
        "<h1>Background Removal QA Review</h1>"
        f"<p>Total images: {len(entries)}</p>"
        "<table><tr><th>Code</th><th>Before</th><th>After</th></tr>"
        + "\n".join(rows)
        + "</table></body></html>"
    )
    (qa_dir / "report.html").write_text(html, encoding="utf-8")
    return len(entries)


def load_series_info(csv_path: Path) -> dict[str, dict]:
    """Load series_codes.csv into a dict keyed by Series Code."""
    result: dict[str, dict] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = row["Series Code"].strip()
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


def main(qa_mode: bool = False, qa_filter: list[str] | None = None) -> int:
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

    if qa_mode:
        qa_dir = root / "qa-review"
        count = generate_qa_report(images_dir, qa_dir, filter_codes=qa_filter)
        print(f"QA report: processed {count} images")
        print(f"Open {qa_dir / 'report.html'} to review")
        return 0

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
    import argparse

    parser = argparse.ArgumentParser(description="Build vehicle image pipeline")
    parser.add_argument("--qa", action="store_true", help="Generate QA review report only")
    parser.add_argument("--qa-filter", nargs="+", metavar="CODE", help="Only QA these codes (e.g. --qa-filter bz4 rav cor)")
    args = parser.parse_args()
    sys.exit(main(qa_mode=args.qa, qa_filter=args.qa_filter))
