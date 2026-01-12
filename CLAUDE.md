# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Extracts Pakistan's Tax Directory PDFs (2013-2018) into CSV/Parquet formats with web visualizations. See README.md for dataset statistics.

## Architecture

**Data pipeline:**
```
PDF → [extract_fast.sh YEAR] → CSV → [create_parquet_python.py YEAR] → Parquet
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
uv run --with duckdb scripts/create_parquet_python.py 2018     # CSV → Parquet

# Extract all years
for year in 2013 2014 2015 2016 2017 2018; do
  bash scripts/extract_fast.sh $year
  uv run --with duckdb scripts/create_parquet_python.py $year
done

# Generate web data
uv run scripts/generate_web_data.py                             # Parquet → JSON
```

**Note:** Query examples are in README.md.

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
