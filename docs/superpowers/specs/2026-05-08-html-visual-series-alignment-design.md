# HTML Visual Series Table Alignment Design

**Date:** 2026-05-08
**Approach:** Minimal Migration (A) — direct column swaps, bug fix, add labels

## Context

Three HTML Content Visual DAX measures need alignment with the new `'Series'` dimension table (migrated from `'d_VehicleSpecs'` in commit a910e63). Additionally, all three need a Series Code label added under each vehicle image.

## Measures In Scope

| # | Measure | Current State |
|---|---|---|
| 1 | `Vehicle Image HTML` | Already references `'Series'` table. Missing label. Has latent TOPN bug. |
| 2 | `Series Family Vehicle Image HTML` | Still references `'d_VehicleSpecs'`. Missing label. Broken fallback logic. |
| 3 | `Vehicle Images HTML (Grid)` | Still references `'d_VehicleSpecs'`. No labels shown (SELECTEDVALUE returns BLANK inside CONCATENATEX). |

## Changes

### All Measures: TOPN Sort Bug Fix

The family-fallback expression:
```dax
TOPN(1, VALUES('Series'[Series Code]), 'Series'[Series Sort Order], ASC)
```
Errors because `VALUES('Series'[Series Code])` returns a one-column table — TOPN's row context doesn't include `[Series Sort Order]`.

**Fix:** Wrap in `CALCULATE(MIN(...))` to force context transition:
```dax
TOPN(1, VALUES('Series'[Series Code]), CALCULATE(MIN('Series'[Series Sort Order])), ASC)
```

### Measure 1: Vehicle Image HTML

**File:** `vehicle_images/dax/VehicleImageHTML.dax`

Changes:
- Fix TOPN sort expression (bug fix above)
- Add `flex-direction:column` to outer VehicleHtml container
- Append `<span>` with `CodeRaw` below the image (14px, #555, sans-serif, 6px top margin)

Label shows the resolved code — whether from direct selection or family fallback.

### Measure 2: Series Family Vehicle Image HTML

**Location:** Power BI model (not yet in a .dax file)

Column migrations:
| Old | New |
|---|---|
| `'d_VehicleSpecs'[Series Family]` | `'Series'[Series Family]` |
| `'d_VehicleSpecs'[Series]` | `'Series'[Series Code]` |

CodeRaw logic change — replace broken `MIN()` approach:
```dax
-- Before (alphabetical, wrong):
VAR CodeRaw = CALCULATE(MIN('d_VehicleSpecs'[Series]), REMOVEFILTERS('d_VehicleSpecs'[Series]))

-- After (sort-order aware, correct):
VAR CodeRaw =
    IF (
        HASONEVALUE('Series'[Series Code]),
        SELECTEDVALUE('Series'[Series Code]),
        MINX(
            TOPN(1, VALUES('Series'[Series Code]), CALCULATE(MIN('Series'[Series Sort Order])), ASC),
            'Series'[Series Code]
        )
    )
```

Animation direction: Rank by `'Series'[Series Family]` (family-oriented measure).

Layout: Same label pattern as Measure 1 (flex-direction:column, `<span>` with CodeRaw).

Blank check: `ISBLANK(FamilyRaw) || ISBLANK(CodeRaw)` — unchanged logic.

### Measure 3: Vehicle Images HTML (Grid)

**Location:** Power BI model (not yet in a .dax file)

Column migrations:
| Old | New |
|---|---|
| `d_VehicleSpecs[Series]` | `'Series'[Series Code]` |
| `d_VehicleSpecs[Series Description]` | *(removed)* |

CONCATENATEX fix — replace broken SELECTEDVALUE with direct column reference:
```dax
CONCATENATEX(
    VALUES('Series'[Series Code]),
    VAR CodeRaw = 'Series'[Series Code]
    VAR CodeSafe = LOWER(SUBSTITUTE(CodeRaw, "/", "-"))
    RETURN
        "<figure style='margin:8px;text-align:center;flex:0 0 auto;'>"
            & "<img src='" & BaseUrl & CodeSafe & ".webp' "
                & "style='height:140px;max-width:240px;object-fit:contain;' "
                & "onerror=""this.src='" & BaseUrl & "placeholder.webp'"">"
            & "<figcaption style='font-size:12px;margin-top:4px;'>" & CodeRaw & "</figcaption>"
        & "</figure>",
    ""
)
```

Figcaption shows `CodeRaw` (2-3 character Series Code). Container markup unchanged.

## Label Styling

Consistent across all measures:
- **Single-image measures (1 & 2):** `<span style='font-size:14px;color:#555;font-family:sans-serif;margin-top:6px;'>`
- **Grid measure (3):** `<figcaption style='font-size:12px;margin-top:4px;'>` (slightly smaller to fit tile layout)

## Files to Modify

| File | Action |
|---|---|
| `vehicle_images/dax/VehicleImageHTML.dax` | Edit: fix TOPN bug, add label |
| `vehicle_images/dax/SeriesFamilyVehicleImageHTML.dax` | Create: new file with migrated measure |
| `vehicle_images/dax/VehicleImagesGridHTML.dax` | Create: new file with migrated measure |
| `SalesRecords_Measures_Guide.md` | Edit: update Vehicle Image HTML section to document all three measures |

## Out of Scope

- No changes to the 10 live sales measures (already aligned)
- No changes to Python image pipeline
- No changes to series_codes.csv
