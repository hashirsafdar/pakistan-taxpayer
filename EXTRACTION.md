# Technical Documentation - Data Extraction & Processing

This document describes the technical process for extracting and processing taxpayer data from the FBR PDFs (2013-2018).

## PDF Structure by Year

| Year | PDF Size | Pages | Section | Page Range | Records | Serial # | ID Format | Notes |
|------|----------|-------|---------|------------|---------|----------|-----------|-------|
| **2018** | 229 MB | 35,445 | Companies | 4 - 473 | 44,609 | Yes | ntn_7 | 7-digit NTN |
| | | | AOP | 473 - 1,150 | 64,336 | Yes | ntn_7 | 7-digit NTN |
| | | | Individuals | 1,151 - 35,445 | 2,743,396 | Yes | cnic | 13-digit CNIC (99.8%), some 7-digit |
| **2017** | 148 MB | - | Companies | - | 37,127 | Yes | ntn_7 | 7-digit NTN |
| | | | AOP | - | 53,811 | Yes | ntn_7 | 7-digit NTN |
| | | | Individuals | - | 1,680,396 | Yes | cnic | 13-digit CNIC (99.8%), some 7-digit |
| **2016** | 67 MB | - | Companies | - | 31,361 | No | ntn_8 | 7-digit + check digit |
| | | | AOP | - | 48,364 | No | ntn_8 | 7-digit + check digit |
| | | | Individuals | - | 1,136,880 | No | cnic | Variable length CNIC |
| **2015** | 50 MB | - | Companies | - | 28,097 | No | ntn_8 | 7-digit + check digit |
| | | | AOP | - | 44,600 | No | ntn_8 | 7-digit + check digit |
| | | | Individuals | 1,237 - | 691,259 | No | cnic | Variable length CNIC |
| **2014** | 43 MB | - | Companies | - | 24,186 | No | ntn_8 | 7-digit + check digit |
| | | | AOP | - | 40,764 | No | ntn_8 | 7-digit + check digit |
| | | | Individuals | - | 788,630 | No | cnic | Variable length CNIC |
| **2013** | 49 MB | 16,847 | Company | 4 - ~500 | 23,459 | No | ntn_8 | 7-digit + check digit |
| | | | AOP | ~500 - 1,377 | 40,610 | No | ntn_8 | 7-digit + check digit |
| | | | Individual | 1,377 - 16,847 | 727,064 | No | ntn_8 | **Individuals use NTN, not CNIC** |

**Key Differences:**
- **2017-2018:** Include serial numbers, use 7-digit NTN and predominantly 13-digit CNIC (99.8%, with ~0.2% having 7-digit values)
- **2014-2016:** No serial numbers, use 8-digit NTN and variable-length CNIC (predominantly 13-digit with more variation)
- **2013:** No serial numbers, individuals identified by NTN (not CNIC)

## Data Schema

Schema varies by year based on PDF format:

| Years | Entity Type | Columns | Description |
|-------|-------------|---------|-------------|
| **2017-2018** | Companies | `sr`, `name`, `ntn_7`, `tax_paid` | Serial number + 7-digit NTN |
| | AOP | `sr`, `name`, `ntn_7`, `tax_paid` | Serial number + 7-digit NTN |
| | Individuals | `sr`, `name`, `cnic`, `tax_paid` | Serial number + CNIC (predominantly 13-digit) |
| **2014-2016** | Companies | `name`, `ntn_8`, `tax_paid` | 8-digit NTN (7 + check digit) |
| | AOP | `name`, `ntn_8`, `tax_paid` | 8-digit NTN (7 + check digit) |
| | Individuals | `name`, `cnic`, `tax_paid` | Variable-length CNIC |
| **2013** | Companies | `name`, `ntn_8`, `tax_paid` | 8-digit NTN (7 + check digit) |
| | AOP | `name`, `ntn_8`, `tax_paid` | 8-digit NTN (7 + check digit) |
| | Individuals | `name`, `ntn_8`, `tax_paid` | 8-digit NTN (individuals use NTN, not CNIC) |

**Column Definitions:**
- `sr` - Serial number from PDF (when available)
- `name` - Taxpayer name
- `ntn_7` - 7-digit National Tax Number (2017-2018, truncated)
- `ntn_8` - 8-digit National Tax Number (2013-2016, full with check digit)
  - **Note:** The 8th digit is a check digit that may change over time for the same entity
  - **Always use first 7 digits for searching/filtering across years**
- `cnic` - CNIC (Computerized National Identity Card)
  - 2017-2018: Predominantly 13-digit (99.8%), with small number of 7-digit values
  - 2014-2016: Variable length (7-16 digits), predominantly 13-digit (>98%)
- `tax_paid` - Tax paid in PKR (Pakistan Rupees)

## Extraction Process

### 1. Extract Data from PDF

```bash
# Extract specific year (2013-2018)
bash scripts/extract_fast.sh 2018

# Or extract all years
for year in 2013 2014 2015 2016 2017 2018; do
  bash scripts/extract_fast.sh $year
done
```

This processes PDF pages and creates three CSV files using pdftotext + perl pipeline.

**Output (for each year):**
- `docs/data/YEAR/companies.csv` - Company records
- `docs/data/YEAR/aop.csv` - AOP records
- `docs/data/YEAR/individuals.csv` - Individual records

### 2. Create Parquet Files

```bash
# Create parquet for specific year
uv run --with duckdb scripts/create_parquet_python.py 2018

# Or create for all years
for year in 2013 2014 2015 2016 2017 2018; do
  uv run --with duckdb scripts/create_parquet_python.py $year
done
```

Creates compressed Parquet files using DuckDB. Parquet provides better compression than CSV and is optimized for analytical queries.

**Compression results (2018):**
- `docs/data/2018/companies.parquet` - 1.2 MB (50% smaller than CSV)
- `docs/data/2018/aop.parquet` - 1.5 MB (40% smaller than CSV)
- `docs/data/2018/individuals.parquet` - 45.8 MB (60% smaller than CSV)

### 3. Generate Web Data

```bash
uv run --with duckdb scripts/generate_web_data.py
```

Generates JSON files from Parquet for the GitHub Pages interface:
- `docs/data/statistics.json` - Overall statistics by taxpayer type
- `docs/data/top_taxpayers.json` - Top 100 taxpayers in each category

### 4. Create Consolidated File (Optional)

```bash
uv run --with duckdb scripts/create_consolidated_parquet.py
```

Creates a single consolidated Parquet file combining all years and categories:
- `docs/data/all.parquet` - 8.2M records, 69 MB (ZSTD compressed)

**Consolidated Schema:**
```sql
year         INTEGER     -- 2013-2018
category     VARCHAR     -- 'company', 'aop', 'individual'
name         VARCHAR     -- Taxpayer name (preserved as-is from each year)
id           VARCHAR     -- Raw NTN (7-8 digit) or CNIC (13 digit)
id_type      VARCHAR     -- 'ntn' or 'cnic'
ntn_7        VARCHAR     -- First 7 digits of NTN (NULL for CNIC records)
tax_paid     BIGINT      -- Tax paid in PKR
```

**Name Handling Across Years:**
When the same taxpayer ID (CNIC or NTN) has different name spellings across years, **each year's record preserves its original name**. No normalization or deduplication occurs.

Example:
```sql
-- Same CNIC with different names across years
CNIC 3520223800364:
  2016: "AYSHA ALI"
  2017: "(1802) AYSHA ALI"
  2018: "(1802) AYSHA ALI"
```

This preserves the exact data from each year's FBR publication. To find all name variants for a taxpayer:
```sql
SELECT DISTINCT year, name FROM 'docs/data/all.parquet'
WHERE id = '3520223800364'
ORDER BY year;
```

**Benefits:**
- Simpler cross-year queries (no UNION ALL needed)
- HTTP range request optimization (sorted by `id_type, ntn_7, id, year, category`)
- Pre-computed `ntn_7` column for efficient NTN lookups
- Preserves historical name changes/variations
- **Faster NTN/CNIC lookups**: Single HTTP request instead of 12-18 separate requests
  - NTN lookups skip all CNIC row groups entirely
  - CNIC lookups skip all NTN row groups entirely
  - Row group pruning skips non-matching data blocks

## DuckDB Query Examples

Query Parquet files directly using DuckDB:

```bash
duckdb
```

**Important:** When searching by NTN, use only the **first 7 digits**. The 8th digit is a check digit that may change over time for the same entity.

### Search companies by name (2018)
```sql
SELECT sr, name, ntn_7, tax_paid
FROM 'docs/data/2018/companies.parquet'
WHERE name LIKE '%abbott%'
ORDER BY tax_paid DESC;
```

### Search by NTN (first 7 digits only)
```sql
-- Search across years 2013-2016 using first 7 NTN digits
SELECT '2013' as year, name, ntn_8, tax_paid
FROM 'docs/data/2013/companies.parquet'
WHERE LEFT(CAST(ntn_8 AS VARCHAR), 7) = '9011410'
UNION ALL
SELECT '2014' as year, name, ntn_8, tax_paid
FROM 'docs/data/2014/companies.parquet'
WHERE LEFT(CAST(ntn_8 AS VARCHAR), 7) = '9011410'
UNION ALL
SELECT '2015' as year, name, ntn_8, tax_paid
FROM 'docs/data/2015/companies.parquet'
WHERE LEFT(CAST(ntn_8 AS VARCHAR), 7) = '9011410'
UNION ALL
SELECT '2016' as year, name, ntn_8, tax_paid
FROM 'docs/data/2016/companies.parquet'
WHERE LEFT(CAST(ntn_8 AS VARCHAR), 7) = '9011410'
ORDER BY year;
-- Example: Fisheries Development Board has NTN 90114100 (2013-2014) and 90114108 (2015-2016)
```

### Get total tax by all companies (2018)
```sql
SELECT COUNT(*), SUM(tax_paid)
FROM 'docs/data/2018/companies.parquet'
WHERE tax_paid > 0;
```

### Find individuals with highest tax (2017)
```sql
SELECT sr, name, cnic_13, tax_paid
FROM 'docs/data/2017/individuals.parquet'
ORDER BY tax_paid DESC
LIMIT 50;
```

### Query across multiple years (2014-2016 individuals)
```sql
SELECT '2014' as year, name, cnic_13, tax_paid FROM 'docs/data/2014/individuals.parquet'
UNION ALL
SELECT '2015' as year, name, cnic_13, tax_paid FROM 'docs/data/2015/individuals.parquet'
UNION ALL
SELECT '2016' as year, name, cnic_13, tax_paid FROM 'docs/data/2016/individuals.parquet'
ORDER BY tax_paid DESC
LIMIT 100;
```

## Consolidated File Query Examples

Using the consolidated file (`docs/data/all.parquet`) simplifies cross-year queries:

### Search by NTN across all years
```sql
-- No UNION ALL needed with consolidated file
SELECT * FROM 'docs/data/all.parquet'
WHERE ntn_7 = '0787223'
ORDER BY year;
```

### Top taxpayers across all years (2013-2018)
```sql
SELECT name, ntn_7, SUM(tax_paid) as total
FROM 'docs/data/all.parquet'
WHERE category = 'company'
GROUP BY ntn_7, name
ORDER BY total DESC
LIMIT 10;
```

### Search by CNIC across all years
```sql
SELECT * FROM 'docs/data/all.parquet'
WHERE id_type = 'cnic' AND id = '3520223800364'
ORDER BY year;
```

### Year-over-year statistics
```sql
SELECT year, category, COUNT(*) as count, SUM(tax_paid) as total
FROM 'docs/data/all.parquet'
GROUP BY year, category
ORDER BY year, category;
```

### Find all records for a specific taxpayer name
```sql
SELECT year, category, name, id, tax_paid
FROM 'docs/data/all.parquet'
WHERE name LIKE '%OIL AND GAS DEVELOPMENT%'
ORDER BY year, category;
```

### Find all name variants for a specific taxpayer ID
```sql
-- Track how a taxpayer's name changed across years
SELECT year, name, tax_paid
FROM 'docs/data/all.parquet'
WHERE id = '3520223800364'
ORDER BY year;

-- Result shows name variations:
-- 2016: "AYSHA ALI"
-- 2017: "(1802) AYSHA ALI"
-- 2018: "(1802) AYSHA ALI"
```

## Scripts

### Extraction & Data Processing
- `scripts/extract_fast.sh` - Fast extraction from PDF to CSV files using pdftotext + perl
- `scripts/create_parquet_python.py` - Creates Parquet files using DuckDB (fast, compressed)
- `scripts/generate_web_data.py` - Generates JSON files from Parquet for GitHub Pages
- `scripts/create_consolidated_parquet.py` - Creates consolidated all.parquet from all year/category files

### Data Files (Generated - in `docs/data/YEAR/` folders)
For each year (2013-2018):
- `docs/data/YEAR/companies.csv` - Company taxpayer records
- `docs/data/YEAR/aop.csv` - Association of Persons taxpayer records
- `docs/data/YEAR/individuals.csv` - Individual taxpayer records
- `docs/data/YEAR/companies.parquet` - Compressed company records
- `docs/data/YEAR/aop.parquet` - Compressed AOP records
- `docs/data/YEAR/individuals.parquet` - Compressed individual records

Consolidated file:
- `docs/data/all.parquet` - All 8.2M records (2013-2018, all categories) in unified schema

## Requirements

- Python 3.6+
- `pdftotext` command-line tool (from poppler-utils)
- `duckdb` command-line tool
- `uv` (Python package manager)

## Performance

**File Compression:**
- Individual Parquet files: ~48MB total (vs ~120MB CSV)
- Consolidated file: 69MB (ZSTD compressed)

**Query Performance (DuckDB):**
- Most queries: < 100ms
- Full-text search: Sub-second for name searches
- NTN/CNIC lookups with consolidated file: Single HTTP request vs 12-18 requests
  - Row group pruning skips irrelevant data blocks
  - Sorted by `id_type` enables skipping entire NTN or CNIC sections

**Lookup Performance Comparison:**

| Approach | HTTP Requests | Row Group Pruning | Typical Speed |
|----------|--------------|-------------------|---------------|
| Individual files (old) | 12-18 separate files | Per-file only | ~500-1000ms |
| Consolidated file (new) | 1 file | Cross-dataset skipping | ~100-300ms |

**Why consolidated is faster:**
1. Single HTTP connection vs many parallel connections
2. NTN lookups skip all CNIC row groups (saves ~85% of data)
3. CNIC lookups skip all NTN row groups (saves ~15% of data)
4. Within NTN records, non-matching `ntn_7` row groups are skipped
