# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Extracts Pakistan's Tax Directory PDFs (2017 & 2018) into CSV/Parquet formats with web visualizations.

**Three entity types:** Companies (7-digit NTN), AOP (7-digit NTN), Individuals (13-digit CNIC)
- **2018:** 44k companies, 64k AOP, 2.7M individuals
- **2017:** 40k companies, 54k AOP, 1.7M individuals

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
# Full extraction pipeline for 2018
bash scripts/extract_fast.sh 2018                              # PDF → CSV
bash scripts/create_parquet_duckdb.sh 2018                     # CSV → Parquet

# Full extraction pipeline for 2017
bash scripts/extract_fast.sh 2017                              # PDF → CSV
bash scripts/create_parquet_duckdb.sh 2017                     # CSV → Parquet

# Generate web data
uv run scripts/generate_web_data.py                             # Parquet → JSON

# Query examples (2018)
duckdb -c "SELECT * FROM 'data/companies_2018.parquet' LIMIT 10;"
duckdb -c "SELECT * FROM 'data/individuals_2018.parquet' WHERE tax_paid > 100000 LIMIT 5;"

# Query examples (2017)
duckdb -c "SELECT * FROM 'data/companies_2017.parquet' LIMIT 10;"
duckdb -c "SELECT * FROM 'data/individuals_2017.parquet' WHERE tax_paid > 100000 LIMIT 5;"
```

## Key Details

**PDF extraction logic (`extract_fast.sh`):**
- Pattern: `^\s*(\d+)\s+(.+?)\s+(\d{7,13})\s+([-\d,]+)\s*$`
- Distinguishes entities by: regno length (7=NTN, 13=CNIC) + section header detection (companies vs AOP)

**Database schema note:**
- `individuals` table has non-standard column order (sr, name, cnic) - intentional for existing data

**Python:** Uses `uv` for dependencies - scripts use `#!/usr/bin/env -S uvx --with duckdb python3`

**Requirements:** pdftotext (poppler-utils), uv, Python 3.6+
