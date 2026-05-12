"""Generate animated HTML for the Power BI vehicle image visual.

This module is the single source of truth for the HTML template logic.
The DAX measure in Power BI mirrors this logic using string concatenation.
"""

import math

from build import WEB_URL_BASE, slug_for_code

CSS_BLOCK = """\
<style>
@keyframes slide-from-left {
    from { transform: translateX(-100%); opacity: 0; }
    to   { transform: translateX(0);     opacity: 1; }
}
@keyframes slide-from-right {
    from { transform: translateX(100%); opacity: 0; }
    to   { transform: translateX(0);    opacity: 1; }
}
@keyframes fade-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}
</style>"""

GRID_CSS_BLOCK = """\
<style>
@keyframes fade-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}
</style>"""

PLACEHOLDER_HTML = (
    "<div style='display:flex;justify-content:center;align-items:center;"
    "height:100%;animation:fade-in 0.5s ease-out forwards;'>"
    "<span style='color:#999;font-size:18px;font-family:sans-serif;'>"
    "Select a Vehicle</span></div>"
)

NO_VEHICLES_HTML = (
    "<div style='display:flex;justify-content:center;align-items:center;"
    "height:100%;'>"
    "<span style='color:#999;font-size:18px;font-family:sans-serif;'>"
    "No vehicles</span></div>"
)


def _slide_direction(sort_index: int, total_count: int) -> str:
    """Return CSS animation name based on position in the sorted lineup."""
    midpoint = total_count / 2
    return "slide-from-left" if sort_index <= midpoint else "slide-from-right"


def grid_column_count(n: int) -> int:
    """Return the number of grid columns for *n* vehicles.

    Mirrors the DAX SWITCH(TRUE(), ...) lookup in VehicleImagesGridHTML.dax.
    """
    if n <= 3:
        return n
    if n == 4:
        return 2
    if n <= 6:
        return 3
    if n <= 8:
        return 4
    if n == 9:
        return 3
    return 4


def grid_row_count(n: int, cols: int) -> int:
    """Return the number of grid rows: ceil(n / cols)."""
    return math.ceil(n / cols)


def generate_vehicle_grid_html(
    codes: list[str],
    sort_indexes: dict[str, int] | None = None,
    total_count: int = 0,
    base_url: str = WEB_URL_BASE,
) -> str:
    """Render the full grid HTML for a list of series codes.

    Branches by len(codes):
    - 0:     "No vehicles" placeholder
    - 1:     Full-bleed with slide animation (matches VehicleImageHTML.dax)
    - 2-12:  Responsive CSS Grid
    - >12:   Legacy fixed-size tiles
    """
    n = len(codes)
    if sort_indexes is None:
        sort_indexes = {}

    # N = 0: no vehicles placeholder
    if n == 0:
        return CSS_BLOCK + NO_VEHICLES_HTML

    # N = 1: full-bleed single vehicle with slide animation
    if n == 1:
        code = codes[0]
        slug = slug_for_code(code)
        img_url = base_url + slug + ".webp"
        si = sort_indexes.get(code, 1)
        direction = _slide_direction(si, total_count)
        return CSS_BLOCK + (
            "<div style='display:flex;flex-direction:column;justify-content:center;"
            "align-items:center;height:100%;overflow:hidden;'>"
            f"<div style='animation:{direction} 0.4s ease-out forwards;'>"
            f"<img src='{img_url}' "
            "style='max-width:100%;max-height:100%;object-fit:contain;'>"
            "</div>"
            f"<span style='font-size:14px;color:#555;font-family:sans-serif;"
            f"margin-top:6px;'>{code}</span>"
            "</div>"
        )

    # N = 2-12: responsive CSS Grid
    if n <= 12:
        cols = grid_column_count(n)
        rows = grid_row_count(n, cols)
        tiles = []
        for code in codes:
            slug = slug_for_code(code)
            img_url = base_url + slug + ".webp"
            tiles.append(
                "<figure style='margin:4px;display:flex;flex-direction:column;"
                "align-items:center;justify-content:center;"
                "width:100%;height:100%;min-width:0;min-height:0;'>"
                f"<img src='{img_url}' "
                "style='max-width:100%;max-height:100%;object-fit:contain;"
                "flex:1 1 auto;min-width:0;min-height:0;' "
                f"onerror=\"this.src='{base_url}placeholder.webp'\">"
                f"<figcaption style='font-size:12px;color:#555;"
                "font-family:sans-serif;margin-top:4px;max-width:100%;"
                f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                f"{code}</figcaption>"
                "</figure>"
            )
        grid_html = (
            f"<div style='display:grid;"
            f"grid-template-columns:repeat({cols},minmax(0,1fr));"
            f"grid-template-rows:repeat({rows},minmax(0,1fr));"
            "height:100%;overflow:hidden;"
            "animation:fade-in 0.4s ease-out forwards;'>"
            + "".join(tiles)
            + "</div>"
        )
        return GRID_CSS_BLOCK + grid_html

    # N > 12: legacy fixed-size tile layout (current behaviour)
    tiles = []
    for code in codes:
        slug = slug_for_code(code)
        img_url = base_url + slug + ".webp"
        tiles.append(
            "<figure style='margin:8px;text-align:center;flex:0 0 auto;'>"
            f"<img src='{img_url}' "
            "style='height:140px;max-width:240px;object-fit:contain;' "
            f"onerror=\"this.src='{base_url}placeholder.webp'\">"
            f"<figcaption style='font-size:12px;margin-top:4px;'>"
            f"{code}</figcaption>"
            "</figure>"
        )
    legacy_html = (
        "<div style='display:flex;flex-wrap:wrap;"
        "justify-content:center;align-items:flex-start;'>"
        + "".join(tiles)
        + "</div>"
    )
    return legacy_html


def generate_vehicle_html(
    code: str | None,
    sort_index: int | None = None,
    total_count: int = 0,
    base_url: str = WEB_URL_BASE,
) -> str:
    """Generate the full HTML string for the vehicle image visual.

    Args:
        code: Raw series code (e.g., "CAH", "L/C") or None/empty for placeholder.
        sort_index: Alphabetical rank of the series (1-based). Computed via
            RANKX(ALL(...)) in DAX -- no calculated column needed.
        total_count: Total number of distinct series codes (via COUNTROWS(ALL(...))).
        base_url: Base URL for image hosting.

    Returns:
        Complete HTML string with inline CSS animations.
    """
    if not code:
        return CSS_BLOCK + PLACEHOLDER_HTML

    slug = slug_for_code(code)
    img_url = base_url + slug + ".webp"
    direction = _slide_direction(sort_index, total_count)

    vehicle_html = (
        "<div style='display:flex;justify-content:center;align-items:center;"
        "height:100%;overflow:hidden;'>"
        f"<div style='animation:{direction} 0.4s ease-out forwards;'>"
        f"<img src='{img_url}' "
        "style='max-width:100%;max-height:100%;object-fit:contain;'>"
        "</div></div>"
    )
    return CSS_BLOCK + vehicle_html
