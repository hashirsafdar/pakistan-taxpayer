# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Extracts Pakistan's 2018 Tax Directory PDF (229MB, 35,445 pages) into CSV/Parquet formats with web visualizations.

**Three entity types:** Companies (44k, 7-digit NTN), AOP (64k, 7-digit NTN), Individuals (2.7M, 13-digit CNIC)

## Architecture

**Data pipeline:**
```
PDF → [extract_fast.sh] → CSV → [create_parquet_duckdb.sh] → Parquet → [generate_web_data.py] → JSON
```

**File structure:**
- `data/` - All generated files (gitignored): CSV, Parquet, source PDF
- `docs/` - GitHub Pages with symlinks to `../data/*.parquet`
  - `index.html` - Pre-computed stats from JSON
  - `query.html` - Live SQL via DuckDB-WASM loading Parquet over HTTP

## Common Commands

```bash
# Full extraction pipeline
bash scripts/extract_fast.sh                                    # PDF → CSV
bash scripts/create_parquet_duckdb.sh     # CSV → Parquet
uv run scripts/generate_web_data.py                             # Parquet → JSON

# Query examples
python3 scripts/query_taxpayers.py name "abbott" company 10
python3 scripts/query_taxpayers.py regno 1347561
python3 scripts/query_taxpayers.py top all 100
python3 scripts/query_taxpayers.py range 1000000 10000000 company 50
duckdb -c "SELECT * FROM 'data/companies.parquet' LIMIT 10;"
```

## Key Details

**PDF extraction logic (`extract_fast.sh`):**
- Pattern: `^\s*(\d+)\s+(.+?)\s+(\d{7,13})\s+([-\d,]+)\s*$`
- Distinguishes entities by: regno length (7=NTN, 13=CNIC) + section header detection (companies vs AOP)

**Database schema note:**
- `individuals` table has non-standard column order (sr, name, cnic) - intentional for existing data

**Python:** Uses `uv` for dependencies - scripts use `#!/usr/bin/env -S uvx --with duckdb python3`

**Requirements:** pdftotext (poppler-utils), uv, Python 3.6+
