# Technical Documentation - Data Extraction & Processing

This document describes the technical process for extracting and processing taxpayer data from the FBR PDF.

## PDF Structure

The PDF contains three distinct sections:

1. **COMPANIES** (Page 4 - 473)
   - 44,609 records
   - Uses 7-digit NTN (National Tax Number)

2. **ASSOCIATION OF PERSONS (AOP)** (Page 473 - 1150)
   - 64,336 records
   - Uses 7-digit NTN (National Tax Number)

3. **INDIVIDUALS** (Page 1151 - 35445)
   - 2,738,407 records
   - Uses 13-digit CNIC (Computerized National Identity Card)

## Data Schema

### Companies & AOP
- `sr` - Serial number from PDF
- `name` - Taxpayer name
- `ntn` - 7-digit National Tax Number (unique identifier)
- `tax_paid` - Tax paid in PKR

### Individuals
- `sr` - Serial number from PDF
- `name` - Taxpayer name
- `cnic` - 13-digit CNIC (unique identifier)
- `tax_paid` - Tax paid in PKR

## Extraction Process

### 1. Extract Data from PDF

```bash
bash scripts/extract_fast.sh
```

This processes all 35,445 pages and creates three CSV files using pdftotext + perl pipeline.

**Output:**
- `data/companies.csv` - 44,609 company records
- `data/aop.csv` - 64,336 AOP records
- `data/individuals.csv` - 2,738,407 individual records

### 2. Create Parquet Files

```bash
bash scripts/create_parquet_duckdb.sh
```

Creates compressed Parquet files using DuckDB. Parquet provides better compression than CSV and is optimized for analytical queries.

**Compression results:**
- `data/companies.parquet` - 1.2 MB (49.7% smaller than CSV)
- `data/aop.parquet` - 1.5 MB (40.0% smaller than CSV)
- `data/individuals.parquet` - 45.8 MB (59.9% smaller than CSV)

### 3. Generate Web Data

```bash
uv run scripts/generate_web_data.py
```

Generates JSON files from Parquet for the GitHub Pages interface:
- `docs/data/statistics.json` - Overall statistics by taxpayer type
- `docs/data/top_taxpayers.json` - Top 100 taxpayers in each category

## DuckDB Query Examples

Query Parquet files directly using DuckDB:

```bash
duckdb
```

### Search companies by name
```sql
SELECT name, ntn, tax_paid
FROM 'data/companies.parquet'
WHERE name LIKE '%abbott%'
ORDER BY tax_paid DESC;
```

### Get total tax by all companies
```sql
SELECT COUNT(*), SUM(tax_paid)
FROM 'data/companies.parquet'
WHERE tax_paid > 0;
```

### Find individuals with highest tax
```sql
SELECT name, cnic, tax_paid
FROM 'data/individuals.parquet'
ORDER BY tax_paid DESC
LIMIT 50;
```

### Get statistics
```sql
SELECT
    COUNT(*) as total_taxpayers,
    SUM(tax_paid) as total_tax,
    AVG(tax_paid) as avg_tax,
    MAX(tax_paid) as max_tax
FROM 'data/companies.parquet';
```

## Scripts

### Extraction & Data Processing
- `scripts/extract_fast.sh` - Fast extraction from PDF to CSV files using pdftotext + perl
- `scripts/create_parquet_duckdb.sh` - Creates Parquet files using DuckDB (fast, compressed)
- `scripts/generate_web_data.py` - Generates JSON files from Parquet for GitHub Pages

### Data Files (Generated - in `data/` folder)
- `data/companies.csv` - Company taxpayer records
- `data/aop.csv` - Association of Persons taxpayer records
- `data/individuals.csv` - Individual taxpayer records
- `data/companies.parquet`, `data/aop.parquet`, `data/individuals.parquet` - Compressed Parquet files

## Requirements

- Python 3.6+
- `pdftotext` command-line tool (from poppler-utils)
- `duckdb` command-line tool
- `uv` (Python package manager)

## Performance

- Parquet file sizes: ~48MB total (vs ~120MB CSV)
- Query response time: < 100ms for most queries using DuckDB
- Full-text search: Sub-second for name searches
- Handles millions of records efficiently
