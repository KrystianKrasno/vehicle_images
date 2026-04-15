"""Generate animated HTML for the Power BI vehicle image visual.

This module is the single source of truth for the HTML template logic.
The DAX measure in Power BI mirrors this logic using string concatenation.
"""

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

PLACEHOLDER_HTML = (
    "<div style='display:flex;justify-content:center;align-items:center;"
    "height:100%;animation:fade-in 0.5s ease-out forwards;'>"
    "<span style='color:#999;font-size:18px;font-family:sans-serif;'>"
    "Select a Vehicle</span></div>"
)


def _slide_direction(sort_index: int, total_count: int) -> str:
    """Return CSS animation name based on position in the sorted lineup."""
    midpoint = total_count / 2
    return "slide-from-left" if sort_index <= midpoint else "slide-from-right"


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
