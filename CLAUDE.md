# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Extracts Pakistan's Tax Directory PDFs (2013-2018) into CSV/Parquet formats with web visualizations.

**Total dataset:** 8.2M+ taxpayer records across 6 years

**Three entity types:** Companies (NTN), AOP (NTN), Individuals (CNIC or NTN)

| Year | Companies | AOP | Individuals | Format |
|------|-----------|-----|-------------|--------|
| 2018 | 44k | 64k | 2.7M | Serial + ntn_7/cnic |
| 2017 | 37k | 54k | 1.7M | Serial + ntn_7/cnic |
| 2016 | 31k | 48k | 1.1M | ntn_8/cnic |
| 2015 | 28k | 45k | 691k | ntn_8/cnic |
| 2014 | 24k | 41k | 789k | ntn_8/cnic |
| 2013 | 23k | 41k | 727k | ntn_8 (individuals use NTN) |

## Architecture

**Data pipeline:**
```
PDF → [extract_fast.sh YEAR] → CSV → [create_parquet_duckdb.sh YEAR] → Parquet
```

**File structure:**
- `docs/data/YEAR/` - All generated files per year (gitignored CSV, committed Parquet, source PDF)
  - `YEAR/companies.parquet` - Company records
  - `YEAR/aop.parquet` - AOP records
  - `YEAR/individuals.parquet` - Individual records
- `docs/` - GitHub Pages
  - `index.html` - Pre-computed stats from JSON
  - `query.html` - Live SQL via DuckDB-WASM loading Parquet over HTTP

## Common Commands

```bash
# Extract specific year (2013-2018)
bash scripts/extract_fast.sh 2018                              # PDF → CSV
bash scripts/create_parquet_duckdb.sh 2018                     # CSV → Parquet

# Extract all years
for year in 2013 2014 2015 2016 2017 2018; do
  bash scripts/extract_fast.sh $year
  bash scripts/create_parquet_duckdb.sh $year
done

# Generate web data
uv run scripts/generate_web_data.py                             # Parquet → JSON

# Query examples (single year)
duckdb -c "SELECT * FROM 'docs/data/2018/companies.parquet' LIMIT 10;"
duckdb -c "SELECT * FROM 'docs/data/2017/individuals.parquet' WHERE tax_paid > 100000 LIMIT 5;"

# Query examples (multi-year)
duckdb -c "SELECT '2013' as year, * FROM 'docs/data/2013/individuals.parquet'
           UNION ALL
           SELECT '2014' as year, * FROM 'docs/data/2014/individuals.parquet'
           ORDER BY tax_paid DESC LIMIT 100;"
```

## Key Details

**PDF extraction logic (`extract_fast.sh`):**
- Auto-detects year format (2013-2016 no serial numbers, 2017-2018 with serial numbers)
- Pattern matching: `^\s*(\d+)?\s*(.+?)\s+(\d{7}[-\d]*|\d{13}[-\d]*)\s+([-\d,]+)\s*$`
- Distinguishes entities by:
  - Section headers: "COMPANY", "ASSOCIATION OF PERSONS?", "INDIVIDUAL(S)"
  - ID classification by section and length (individuals with any ID length go to individuals file)
  - Exception: 2013 individuals use 8-digit NTN instead of CNIC
- Removes hyphens from IDs, stores as-is (variable length CNICs preserved)

**Schema variations by year:**
- **2017-2018:** `sr, name, ntn_7/cnic, tax_paid` (serial numbers, CNIC is predominantly 13-digit)
- **2014-2016:** `name, ntn_8/cnic, tax_paid` (no serial, CNIC is variable length)
- **2013:** `name, ntn_8, tax_paid` for all types (individuals use NTN)

**Special cases:**
- 2013 individuals identified by NTN (not CNIC)

**Python:** Uses `uv` for dependencies

**Requirements:** pdftotext (poppler-utils), uv, Python 3.6+
