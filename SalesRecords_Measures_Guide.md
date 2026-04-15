# Sales Records Measure Guide

## Purpose

This guide documents the DAX measure set for the `Sales Records` dashboard. It explains what each measure is doing, when to use it, and how the record-comparison logic works at annual grain.

## Model Assumptions

- Base sales measure: `[1965_Sales]`
- Fact table: `'Sales 1965-Date - Load'`
- Calendar table: `'d_Dates'`
- Calendar date column: `'d_Dates'[Dates]`
- Calendar year column: `'d_Dates'[Year]`
- Vehicle dimension: `'d_VehicleSpecs'`
- Series field: `'d_VehicleSpecs'[Series]`
- Series family field: `'d_VehicleSpecs'[Series Family]`
- Luxury type field: `'d_VehicleSpecs'[Luxury Type]`
- Active flag field: `'d_VehicleSpecs'[Active Flag]`

## Context-Aware Design

All measures are context-aware. The same measure produces different results depending on visual context:

- On a card with no series selected, it returns the overall value
- In a table by `Series`, it returns the value for each series
- In a table by `Series Family`, it returns the value for each family
- With slicers like `Luxury Type` or `Active Flag`, it recalculates within that filtered set

There is no need for separate "Series" or "Family" prefixed copies of core or record-chase measures. One set covers all grains.

## Record Logic

"Upcoming records" compares the last available year's sales against the best prior annual record. Because the fact data is only at year level, there are no same-date or YTD pace measures.

The record-chase measures (`Prior Full-Year Record Year`, `Gap to Full-Year Record`, etc.) work identically at any grain:

- On a KPI card: compares overall latest year vs overall best prior year
- In a Series table: compares each series' latest year vs that series' best prior year
- In a Series Family table: compares each family's latest year vs that family's best prior year

## Measure Catalog

### Core Measures

| Measure | Purpose | Best Use |
|---|---|---|
| `1965_Sales` | Base sales measure (sums from fact table) | All visuals |
| `Lifetime Sales` | Total sales across all dates (ignores date filters) | KPI, ranking |
| `Last Sales Year` | Most recent year with sales in current context | KPI, record logic |
| `Last Year Sales` | Sales in the last year | KPI, record gap |
| `Prior Year Sales` | Sales in the year before last | YoY comparison |
| `YoY Change vs Prior Year` | Absolute year-over-year change | KPI, narrative |
| `YoY % vs Prior Year` | Percent year-over-year change | KPI, trend callout |
| `First Sale Year` | Earliest year with sales in current context | KPI, narrative |
| `Best Sales Year` | Year with highest sales in current context | KPI, narrative |
| `Best Sales Value` | Sales amount in the best year | KPI, annotation |
| `Active Series Count` | Count of series with any historical sales | KPI |

### Ranking Measures

| Measure | Purpose | Best Use |
|---|---|---|
| `Top Series Name` | Highest-selling series all-time | KPI, narrative |
| `Top Series Sales` | Lifetime sales for the top series | KPI, narrative |
| `Top Series Family Name` | Highest-selling series family all-time | KPI, narrative |
| `Top Series Family Sales` | Lifetime sales for the top family | KPI, narrative |
| `Series Rank by Lifetime Sales` | Dense rank of each series by lifetime sales | Bar chart, table |
| `Series Family Rank by Lifetime Sales` | Dense rank of each family by lifetime sales (ISINSCOPE guarded) | Bar chart, table |

### Record-Chase Measures

These work at any grain (overall, series, or family) depending on the visual's filter context.

| Measure | Purpose | Best Use |
|---|---|---|
| `Prior Full-Year Record Year` | Best completed historical year before the latest year | Narrative |
| `Prior Full-Year Record Sales` | Sales in that best completed year | KPI, narrative |
| `Gap to Full-Year Record` | Difference between prior record and latest year sales | KPI, headline |
| `Sales Needed to Break Full-Year Record` | Positive amount needed to exceed the record (+1 for strict break) | KPI, narrative |
| `Pct to Full-Year Record` | Latest year sales divided by prior record sales | Gauge, KPI |
| `Overall Record Status` | Text classification: Record Broken, Tied Record, Near Record, Below Record, No Prior Record | Narrative, table |

### Narrative Measures

| Measure | Purpose | Best Use |
|---|---|---|
| `First Sale Lead Series` | Leading series in the first sale year | Narrative |
| `Narrative - Best Sales Year` | Sentence describing the best year and value | Narrative card |
| `Narrative - First Sale` | Sentence describing the first sale year and lead series | Narrative card |
| `Narrative - Top Series` | Sentence describing the all-time top series | Narrative card |
| `Narrative - Upcoming Record` | Sentence describing record status and gap (overall context) | Narrative card |
| `Narrative - Top Series Family` | Sentence describing the all-time top family | Narrative card |
| `Narrative - Series Family Best Year` | Sentence describing the family's best year (uses SELECTEDVALUE) | Narrative card |
| `Narrative - Series Family Upcoming Record` | Sentence describing family record status (uses SELECTEDVALUE) | Narrative card |

## Which Record Measure To Use

| Question | Best Measure |
|---|---|
| What was the best sales year ever? | `Best Sales Year`, `Best Sales Value` |
| What is the all-time annual record? | `Prior Full-Year Record Sales` |
| How far is the current year from the record? | `Gap to Full-Year Record` |
| Which series is closest to its own record? | `Gap to Full-Year Record` in a Series table, `Overall Record Status` |
| What should I use for an upcoming records story? | `Sales Needed to Break Full-Year Record`, `Overall Record Status`, `Narrative - Upcoming Record` |

## Recommended Visual Mapping

| Visual | Recommended Measures |
|---|---|
| KPI cards | `Lifetime Sales`, `Best Sales Year`, `Best Sales Value`, `First Sale Year`, `Top Series Name` |
| Annual trend chart | `1965_Sales` by `d_Dates[Year]`, annotated with `Best Sales Year` |
| Top series ranking | `Lifetime Sales`, `Series Rank by Lifetime Sales` |
| Top family ranking | `Lifetime Sales`, `Series Family Rank by Lifetime Sales` |
| Records table (by series) | `Best Sales Year`, `Best Sales Value`, `Last Year Sales`, `Gap to Full-Year Record`, `Overall Record Status` |
| Records table (by family) | Same measures — context handles the grain |
| Upcoming records panel | `Last Year Sales`, `Prior Full-Year Record Sales`, `Gap to Full-Year Record`, `Sales Needed to Break Full-Year Record` |
| Narrative text cards | `Narrative - Best Sales Year`, `Narrative - First Sale`, `Narrative - Top Series`, `Narrative - Upcoming Record` |

## Gap Sign Convention

The base measures use `Record - Current` (positive = still below). A patch file (`GapMeasures_Negative_Patch.dax`) flips the convention to `Current - Record` (positive = record broken). The patch redefines only three measures: `Gap to Full-Year Record`, `Sales Needed to Break Full-Year Record`, and `Overall Record Status`. All other measures (narratives, pct, etc.) consume these and produce correct results automatically.

## Suggested Simplification

If the page starts to feel too dense, keep these as the core production set:

- `Lifetime Sales`
- `Best Sales Year`
- `Best Sales Value`
- `First Sale Year`
- `Top Series Name`
- `Series Rank by Lifetime Sales`
- `Last Year Sales`
- `Gap to Full-Year Record`
- `Overall Record Status`

That smaller set will cover most of the one-page storytelling without overbuilding the model.
