# Pakistan Taxpayer Directory 2018 - Data Extraction & Query System

This project extracts taxpayer data from the massive PDF (229MB, 35,445 pages) and converts it into searchable CSV files and SQLite database.

**Data Source:** [Tax Directory of Pakistan 2018](https://opendata.com.pk/dataset/tax-directory-of-pakistan-2018) - Published by Federal Board of Revenue (FBR) Pakistan on 18th September 2020.

**Live Demo:** [Explore the dataset online](https://old.hashirsafdar.com/pakistan-taxpayer/)

## Files

### Extraction & Database Creation
- `extract_taxpayer_data.py` - Extracts data from PDF to CSV files
- `create_database.py` - Creates SQLite database and loads CSV data
- `query_taxpayers.py` - Query interface for searching the database

### Data Files (Generated)
- `companies.csv` - All company/organization taxpayer records
- `individuals.csv` - All individual taxpayer records
- `taxpayers.db` - SQLite database with indexed tables

## Data Structure

### Companies Table
- Serial Number
- Taxpayer Name
- Registration Number (7 digits)
- Tax Paid

### Individuals Table
- Serial Number
- Taxpayer Name
- Registration Number (13 digits)
- Tax Paid

## Usage

### 1. Extract Data from PDF (Long Running)

```bash
python3 extract_taxpayer_data.py
```

This processes all 35,445 pages and creates two CSV files. Expected time: 1-3 hours depending on system.

### 2. Create SQLite Database

```bash
python3 create_database.py
```

Loads CSV data into SQLite with proper indexes for fast queries.

### 3. Query the Database

#### Search by Name
```bash
python3 query_taxpayers.py name "abbott" company 10
python3 query_taxpayers.py name "shaikh" individual 20
python3 query_taxpayers.py name "limited" all 50
```

#### Search by Registration Number
```bash
python3 query_taxpayers.py regno 1347561
python3 query_taxpayers.py regno 4230128739899
```

#### Get Top Taxpayers
```bash
python3 query_taxpayers.py top company 20
python3 query_taxpayers.py top individual 50
python3 query_taxpayers.py top all 100
```

#### Search by Tax Range
```bash
python3 query_taxpayers.py range 1000000 10000000 company 50
python3 query_taxpayers.py range 500000 1000000 individual 100
```

## Direct SQL Queries

You can also query directly using sqlite3:

```bash
sqlite3 taxpayers.db

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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sr_no INTEGER,
    name TEXT NOT NULL,
    registration_no TEXT,
    tax_paid REAL,
    UNIQUE(sr_no, registration_no)
);

CREATE TABLE individuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sr_no INTEGER,
    name TEXT NOT NULL,
    registration_no TEXT,
    tax_paid REAL,
    UNIQUE(sr_no, registration_no)
);
```

With indexes on:
- `name` (for name searches)
- `registration_no` (for exact lookups)
- `tax_paid` (for range queries and sorting)

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
