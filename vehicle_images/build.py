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
