# Pakistan Taxpayer Directory 2018 - Data Extraction & Query System

This project extracts taxpayer data from the massive PDF (229MB, 35,445 pages) and converts it into searchable CSV files and SQLite database.

**Data Source:** [Tax Directory of Pakistan 2018](https://opendata.com.pk/dataset/tax-directory-of-pakistan-2018) - Published by Federal Board of Revenue (FBR) Pakistan on 18th September 2020.

**Live Demo:** [Explore the dataset online](https://old.hashirsafdar.com/pakistan-taxpayer/)

**Interactive Queries:** [Run SQL queries in your browser](https://old.hashirsafdar.com/pakistan-taxpayer/query.html) - Powered by DuckDB-WASM

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

## Files

### Extraction & Database Creation
- `scripts/extract_fast.sh` - Fast extraction from PDF to CSV files using pdftotext + perl
- `scripts/create_database.py` - Creates SQLite database using native .import (fast)
- `scripts/create_parquet_duckdb.py` - Creates Parquet files using DuckDB (fast, compressed)
- `scripts/generate_web_data.py` - Generates JSON files for GitHub Pages

### Data Files (Generated - in `data/` folder)
- `data/companies.csv` - Company taxpayer records
- `data/aop.csv` - Association of Persons taxpayer records
- `data/individuals.csv` - Individual taxpayer records
- `data/taxpayers.db` - SQLite database with 3 tables
- `data/companies.parquet`, `data/aop.parquet`, `data/individuals.parquet` - Compressed Parquet files

## Data Structure

### Companies Table
- `ntn` (PRIMARY KEY) - National Tax Number (7 digits)
- `sr` - Serial number from PDF
- `name` - Taxpayer Name
- `tax_paid` - Tax Paid (PKR)

### Association of Persons (AOP) Table
- `ntn` (PRIMARY KEY) - National Tax Number (7 digits)
- `sr` - Serial number from PDF
- `name` - Taxpayer Name
- `tax_paid` - Tax Paid (PKR)

### Individuals Table
- `cnic` (PRIMARY KEY) - CNIC (13 digits)
- `sr` - Serial number from PDF
- `name` - Taxpayer Name
- `tax_paid` - Tax Paid (PKR)

## Usage

### 1. Extract Data from PDF (Fast)

```bash
bash scripts/extract_fast.sh
```

This processes all 35,445 pages and creates three CSV files using pdftotext + perl pipeline.

### 2. Create SQLite Database

```bash
uv run scripts/create_database.py
```

Uses SQLite's native `.import` command for fast bulk loading.

### 3. Create Parquet Files (Optional)

```bash
uv run scripts/create_parquet_duckdb.py
```

Creates compressed Parquet files using DuckDB. Parquet provides better compression than CSV and is optimized for analytical queries.

### 4. Query the Database

## SQL Queries

Query the database directly using sqlite3:

```bash
sqlite3 data/taxpayers.db

# Search companies by name
SELECT name, registration_no, tax_paid
FROM companies
WHERE name LIKE '%abbott%'
ORDER BY tax_paid DESC;

# Get total tax by all companies
SELECT COUNT(*), SUM(tax_paid)
FROM companies
WHERE tax_paid > 0;

# Find individuals with highest tax
SELECT name, registration_no, tax_paid
FROM individuals
ORDER BY tax_paid DESC
LIMIT 50;

# Get statistics
SELECT
    COUNT(*) as total_taxpayers,
    SUM(tax_paid) as total_tax,
    AVG(tax_paid) as avg_tax,
    MAX(tax_paid) as max_tax
FROM companies;
```

## Database Schema

```sql
CREATE TABLE companies (
    ntn TEXT PRIMARY KEY,
    sr INTEGER,
    name TEXT NOT NULL,
    tax_paid REAL
);

CREATE TABLE aop (
    ntn TEXT PRIMARY KEY,
    sr INTEGER,
    name TEXT NOT NULL,
    tax_paid REAL
);

CREATE TABLE individuals (
    cnic TEXT PRIMARY KEY,
    sr INTEGER,
    name TEXT NOT NULL,
    tax_paid REAL
);
```

No indexes needed - NTN and CNIC are unique government identifiers used as primary keys.

## Performance

- Database size: ~500MB (estimated)
- Query response time: < 100ms for most queries
- Full-text search: Sub-second for name searches
- Handles millions of records efficiently

## Requirements

- Python 3.6+
- `pdftotext` command-line tool (from poppler-utils)
- Standard library only (sqlite3, csv, subprocess)

## Notes

- The PDF has ~9,000+ company records and ~2.3M individual records
- Companies have 7-digit registration numbers
- Individuals have 13-digit registration numbers
- Tax amounts are in Pakistani Rupees (PKR)
- Records with no tax paid are stored as 0
