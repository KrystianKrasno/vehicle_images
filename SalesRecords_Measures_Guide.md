# Sales Records Measure Guide

## Model Assumptions

- Base sales measure: `[1965_Sales]`
- Fact table: `'Sales 1965-Date - Load'`
- Calendar table: `'d_Dates'` with `[Dates]` and `[Year]` columns
- Vehicle dimension: `'Series'` with `[Series Code]`, `[Series Family]`, `[Series Sort Order]`, `[Luxury Type]`, `[Active Flag]`, and others

## Context-Aware Design

All measures are context-aware. The same measure produces different results depending on visual context:

- On a card with no series selected → overall value
- In a table by `Series Code` → per-series value
- In a table by `Series Family` → per-family value
- With slicers (Luxury Type, Active Flag, etc.) → recalculates within that filtered set

One set of measures covers all grains — no separate "Series Family" prefixed copies needed.

## Live Measures (10)

| # | Measure | Purpose |
|---|---|---|
| 1 | `[Lifetime Sales]` | Total sales across all years (ignores date filters) |
| 2 | `[First Sales Year]` | Earliest year with sales in current context |
| 3 | `[Best Sales Year]` | Year with highest sales in current context |
| 4 | `[Best Annual Sales]` | Sales amount in the best year |
| 5 | `[Current Year Sales]` | Sales in the most recent year with data |
| 6 | `[Rank by Lifetime Sales]` | Dense rank — auto-detects Series Code or Family grain via ISINSCOPE |
| 7 | `[YoY %]` | Year-over-year percentage change |
| 8 | `[Overall Record Status]` | Text: Record Broken / Tied Record / Near Record / Below Record / No Prior Record |
| 9 | `[Prior Full-Year Record Year]` | Best completed year before the latest year |
| 10 | `[Gap to Full-Year Record]` | Difference between prior record and current year (positive = still below) |

## Internal Helpers

These are not intended for direct use in visuals but are consumed by the live measures above:

| Helper | Used By |
|---|---|
| `[Last Sales Year]` | `[Current Year Sales]`, `[YoY %]`, record chain |
| `[Prior Year Sales]` | `[YoY %]` |
| `[Prior Full-Year Record Sales]` | `[Overall Record Status]`, `[Gap to Full-Year Record]` |
| `[Pct to Full-Year Record]` | `[Overall Record Status]` |

## Ranking — ISINSCOPE Pattern

The `[Rank by Lifetime Sales]` measure uses `ISINSCOPE` to detect the visual's grain:

- `ISINSCOPE('Series'[Series Code])` → ranks by series code
- `ISINSCOPE('Series'[Series Family])` → ranks by family

This eliminates the need for separate ranking measures.

## Vehicle Image HTML

The `Vehicle Image HTML` measure displays animated vehicle images in the HTML Content visual.

**Family-aware fallback:** When a Series Family is selected (multiple series codes), the measure picks the series with the lowest `[Series Sort Order]` as the representative image. When a single series code is selected, it shows that series' image directly.

**Image URL construction:** Series code → lowercase → replace "/" with "-" → append ".webp" → prepend GitHub Pages base URL.

## Gap Sign Convention

Gap measures use `Prior Record - Current Year` (positive = still below record). The `[Overall Record Status]` measure classifies this into text labels.

## Archived Measures

Previously used measures (narratives, series-specific records, family-prefixed duplicates, etc.) are preserved in the `archive/` directory for reference.

## Recommended Visual Mapping

| Visual | Measures |
|---|---|
| KPI cards | `[Lifetime Sales]`, `[Best Sales Year]`, `[Best Annual Sales]`, `[First Sales Year]` |
| Annual trend chart | `[1965_Sales]` by `d_Dates[Year]` |
| Ranking table/bar | `[Lifetime Sales]`, `[Rank by Lifetime Sales]` |
| Records panel | `[Current Year Sales]`, `[Gap to Full-Year Record]`, `[Prior Full-Year Record Year]`, `[Overall Record Status]` |
| Growth indicator | `[YoY %]` |
