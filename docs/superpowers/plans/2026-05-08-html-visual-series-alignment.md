# HTML Visual Series Table Alignment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align three HTML Content Visual DAX measures with the new `'Series'` dimension table, fix the TOPN sort bug, and add Series Code labels under vehicle images.

**Architecture:** Minimal migration — direct column swaps from `d_VehicleSpecs` to `'Series'`, fix a shared TOPN context-transition bug, and append a `<span>` / `<figcaption>` label to each measure's HTML output. One measure per `.dax` file.

**Tech Stack:** DAX (Power BI / Tabular Editor), Markdown documentation

---

### Task 1: Fix TOPN bug and add label in Vehicle Image HTML

**Files:**
- Modify: `vehicle_images/dax/VehicleImageHTML.dax` (lines 15-17 for bug fix, lines 31-37 for label)

- [ ] **Step 1: Fix the TOPN sort expression**

In `vehicle_images/dax/VehicleImageHTML.dax`, change line 16 from:

```dax
            TOPN ( 1, VALUES ( 'Series'[Series Code] ), 'Series'[Series Sort Order], ASC ),
```

to:

```dax
            TOPN ( 1, VALUES ( 'Series'[Series Code] ), CALCULATE ( MIN ( 'Series'[Series Sort Order] ) ), ASC ),
```

This wraps the sort column in `CALCULATE(MIN(...))` to force a context transition, since `VALUES('Series'[Series Code])` produces a one-column table whose row context doesn't include `[Series Sort Order]`.

- [ ] **Step 2: Add flex-direction:column and Series Code label to VehicleHtml**

Replace the VehicleHtml variable (lines 31-37) with:

```dax
VAR VehicleHtml =
    "<div style='display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;overflow:hidden;'>" &
        "<div style='animation:" & Direction & " 0.4s ease-out forwards;'>" &
            "<img src='" & ImgUrl & "' " &
                "style='max-width:100%;max-height:100%;object-fit:contain;'>" &
        "</div>" &
        "<span style='font-size:14px;color:#555;font-family:sans-serif;margin-top:6px;'>" & CodeRaw & "</span>" &
    "</div>"
```

Changes from the original:
- Added `flex-direction:column` so the label sits below the image
- Appended a `<span>` with `CodeRaw` after the animated image `<div>`

- [ ] **Step 3: Verify the full measure reads correctly**

The complete file should now be:

```dax
-- Measure: Vehicle Image HTML
-- Renders an animated HTML visual for the Power BI HTML Content visual.
-- Slides in from left (first half of alphabet) or right (second half).
-- Shows "Select a Vehicle" prompt when no vehicle is selected.
--
-- Family-aware: when a Series Family is selected (multiple series codes),
-- picks the series with the lowest Series Sort Order as the representative image.

Vehicle Image HTML =
VAR BaseUrl = "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"
VAR CodeRaw =
    IF (
        HASONEVALUE ( 'Series'[Series Code] ),
        SELECTEDVALUE ( 'Series'[Series Code] ),
        MINX (
            TOPN ( 1, VALUES ( 'Series'[Series Code] ), CALCULATE ( MIN ( 'Series'[Series Sort Order] ) ), ASC ),
            'Series'[Series Code]
        )
    )
VAR CodeSafe = LOWER(SUBSTITUTE(CodeRaw, "/", "-"))
VAR ImgUrl = BaseUrl & CodeSafe & ".webp"
VAR SortIdx = RANKX(ALL('Series'[Series Code]), 'Series'[Series Code], CodeRaw, ASC, DENSE)
VAR Total = COUNTROWS(ALL('Series'[Series Code]))
VAR Midpoint = Total / 2
VAR Direction = IF(SortIdx <= Midpoint, "slide-from-left", "slide-from-right")
VAR CssBlock = "<style>@keyframes slide-from-left{from{transform:translateX(-100%);opacity:0}to{transform:translateX(0);opacity:1}}@keyframes slide-from-right{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}@keyframes fade-in{from{opacity:0}to{opacity:1}}</style>"
VAR PlaceholderHtml =
    "<div style='display:flex;justify-content:center;align-items:center;height:100%;animation:fade-in 0.5s ease-out forwards;'>" &
        "<span style='color:#999;font-size:18px;font-family:sans-serif;'>Select a Vehicle</span>" &
    "</div>"
VAR VehicleHtml =
    "<div style='display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;overflow:hidden;'>" &
        "<div style='animation:" & Direction & " 0.4s ease-out forwards;'>" &
            "<img src='" & ImgUrl & "' " &
                "style='max-width:100%;max-height:100%;object-fit:contain;'>" &
        "</div>" &
        "<span style='font-size:14px;color:#555;font-family:sans-serif;margin-top:6px;'>" & CodeRaw & "</span>" &
    "</div>"
RETURN
    CssBlock &
    IF(ISBLANK(CodeRaw), PlaceholderHtml, VehicleHtml)
```

- [ ] **Step 4: Commit**

```bash
git add vehicle_images/dax/VehicleImageHTML.dax
git commit -m "Fix TOPN sort bug; add Series Code label to Vehicle Image HTML"
```

---

### Task 2: Create Series Family Vehicle Image HTML measure

**Files:**
- Create: `vehicle_images/dax/SeriesFamilyVehicleImageHTML.dax`

- [ ] **Step 1: Create the measure file**

Create `vehicle_images/dax/SeriesFamilyVehicleImageHTML.dax` with the full migrated measure:

```dax
-- Measure: Series Family Vehicle Image HTML
-- Renders an animated HTML visual scoped to Series Family selection.
-- Slides in from left (first half of families) or right (second half).
-- Shows "Select a Vehicle" prompt when no family is selected.
--
-- Family-aware fallback: picks the series with the lowest Series Sort Order
-- as the representative image when a family contains multiple series codes.

Series Family Vehicle Image HTML =
VAR BaseUrl =
    "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"
VAR FamilyRaw =
    SELECTEDVALUE ( 'Series'[Series Family] )
VAR CodeRaw =
    IF (
        HASONEVALUE ( 'Series'[Series Code] ),
        SELECTEDVALUE ( 'Series'[Series Code] ),
        MINX (
            TOPN ( 1, VALUES ( 'Series'[Series Code] ), CALCULATE ( MIN ( 'Series'[Series Sort Order] ) ), ASC ),
            'Series'[Series Code]
        )
    )
VAR CodeSafe =
    LOWER ( SUBSTITUTE ( CodeRaw, "/", "-" ) )
VAR ImgUrl =
    BaseUrl & CodeSafe & ".webp"
VAR SortIdx =
    RANKX (
        ALL ( 'Series'[Series Family] ),
        'Series'[Series Family],
        FamilyRaw,
        ASC,
        DENSE
    )
VAR Total =
    COUNTROWS ( ALL ( 'Series'[Series Family] ) )
VAR Midpoint =
    Total / 2
VAR Direction =
    IF ( SortIdx <= Midpoint, "slide-from-left", "slide-from-right" )
VAR CssBlock =
    "<style>@keyframes slide-from-left{from{transform:translateX(-100%);opacity:0}to{transform:translateX(0);opacity:1}}@keyframes slide-from-right{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}@keyframes fade-in{from{opacity:0}to{opacity:1}}</style>"
VAR PlaceholderHtml =
    "<div style='display:flex;justify-content:center;align-items:center;height:100%;animation:fade-in 0.5s ease-out forwards;'>" &
        "<span style='color:#999;font-size:18px;font-family:sans-serif;'>Select a Vehicle</span>" &
    "</div>"
VAR VehicleHtml =
    "<div style='display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;overflow:hidden;'>" &
        "<div style='animation:" & Direction & " 0.4s ease-out forwards;'>" &
            "<img src='" & ImgUrl & "' " &
                "style='max-width:100%;max-height:100%;object-fit:contain;'>" &
        "</div>" &
        "<span style='font-size:14px;color:#555;font-family:sans-serif;margin-top:6px;'>" & CodeRaw & "</span>" &
    "</div>"
RETURN
    CssBlock
        & IF (
            ISBLANK ( FamilyRaw ) || ISBLANK ( CodeRaw ),
            PlaceholderHtml,
            VehicleHtml
        )
```

Key differences from `Vehicle Image HTML`:
- `FamilyRaw` variable to detect family selection
- `SortIdx` ranks by `'Series'[Series Family]` (not Series Code) for animation direction
- Blank check uses `ISBLANK(FamilyRaw) || ISBLANK(CodeRaw)`

- [ ] **Step 2: Commit**

```bash
git add vehicle_images/dax/SeriesFamilyVehicleImageHTML.dax
git commit -m "Add Series Family Vehicle Image HTML measure aligned with Series table"
```

---

### Task 3: Create Vehicle Images HTML (Grid) measure

**Files:**
- Create: `vehicle_images/dax/VehicleImagesGridHTML.dax`

- [ ] **Step 1: Create the measure file**

Create `vehicle_images/dax/VehicleImagesGridHTML.dax` with the full migrated measure:

```dax
-- Measure: Vehicle Images HTML (Grid)
-- Renders a flex-wrap grid of vehicle images for the Power BI HTML Content visual.
-- Each tile shows the vehicle image with its Series Code label underneath.
-- Falls back to placeholder.webp on image load error.

Vehicle Images HTML (Grid) =
VAR BaseUrl = "https://krystiankrasno.github.io/vehicle_images/vehicle_images/images-web/"
VAR Tiles =
    CONCATENATEX (
        VALUES ( 'Series'[Series Code] ),
        VAR CodeRaw = 'Series'[Series Code]
        VAR CodeSafe = LOWER ( SUBSTITUTE ( CodeRaw, "/", "-" ) )
        RETURN
            "<figure style='margin:8px;text-align:center;flex:0 0 auto;'>" &
                "<img src='" & BaseUrl & CodeSafe & ".webp' " &
                    "style='height:140px;max-width:240px;object-fit:contain;' " &
                    "onerror=""this.src='" & BaseUrl & "placeholder.webp'"">" &
                "<figcaption style='font-size:12px;margin-top:4px;'>" & CodeRaw & "</figcaption>" &
            "</figure>",
        ""
    )
RETURN
    "<div style='display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;'>" &
        Tiles &
    "</div>"
```

Key changes from the old measure:
- `d_VehicleSpecs[Series]` → `'Series'[Series Code]`
- Removed broken `SELECTEDVALUE(d_VehicleSpecs[Series Description])` — uses `'Series'[Series Code]` directly as the row value inside CONCATENATEX
- Figcaption shows the 2-3 character Series Code

- [ ] **Step 2: Commit**

```bash
git add vehicle_images/dax/VehicleImagesGridHTML.dax
git commit -m "Add Vehicle Images Grid HTML measure aligned with Series table"
```

---

### Task 4: Update SalesRecords_Measures_Guide.md

**Files:**
- Modify: `SalesRecords_Measures_Guide.md` (lines 56-62, Vehicle Image HTML section)

- [ ] **Step 1: Replace the Vehicle Image HTML section**

Replace lines 56-62 of `SalesRecords_Measures_Guide.md` (the current `## Vehicle Image HTML` section) with:

```markdown
## Vehicle Image HTML Measures

Three measures render vehicle images in HTML Content visuals. All reference the `'Series'` dimension table.

| Measure | Visual Use | File |
|---|---|---|
| `[Vehicle Image HTML]` | Single animated image, context-aware (series or family) | `vehicle_images/dax/VehicleImageHTML.dax` |
| `[Series Family Vehicle Image HTML]` | Single animated image, family-scoped with fallback | `vehicle_images/dax/SeriesFamilyVehicleImageHTML.dax` |
| `[Vehicle Images HTML (Grid)]` | Flex-wrap grid of all series in context | `vehicle_images/dax/VehicleImagesGridHTML.dax` |

**Family-aware fallback:** When multiple series codes are in context (family selection), the single-image measures pick the series with the lowest `[Series Sort Order]` as the representative image via `TOPN` with `CALCULATE(MIN(...))` for context transition.

**Image URL construction:** Series code → lowercase → replace "/" with "-" → append ".webp" → prepend GitHub Pages base URL.

**Series Code label:** All three measures display the resolved Series Code (2-3 characters) centered below each vehicle image.
```

- [ ] **Step 2: Commit**

```bash
git add SalesRecords_Measures_Guide.md
git commit -m "Document all three vehicle image HTML measures in guide"
```

---

### Task 5: Final verification

- [ ] **Step 1: Verify all DAX files exist and are consistent**

Run:
```bash
ls -la vehicle_images/dax/
```

Expected: Three `.dax` files:
- `VehicleImageHTML.dax`
- `SeriesFamilyVehicleImageHTML.dax`
- `VehicleImagesGridHTML.dax`

- [ ] **Step 2: Verify no stale d_VehicleSpecs references remain**

Run:
```bash
grep -ri "d_VehicleSpecs" vehicle_images/dax/
```

Expected: No output (no matches).

- [ ] **Step 3: Verify TOPN bug fix is present in all measures that use it**

Run:
```bash
grep -n "CALCULATE ( MIN ( 'Series'\[Series Sort Order\] ) )" vehicle_images/dax/*.dax
```

Expected: Matches in `VehicleImageHTML.dax` and `SeriesFamilyVehicleImageHTML.dax` (the two measures with family fallback). The Grid measure doesn't use TOPN.

- [ ] **Step 4: Verify Series Code labels are present in all measures**

Run:
```bash
grep -n "CodeRaw" vehicle_images/dax/*.dax
```

Expected: All three files reference `CodeRaw` in their HTML output.
