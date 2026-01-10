# Pakistan Taxpayer Directory 2018

Extracted and processed taxpayer data from the Federal Board of Revenue (FBR) Pakistan's Income Tax Directory 2018.

**Data Source:** [FBR Income Tax Directory](https://fbr.gov.pk/Categ/income-tax-directory/742) - Published by Federal Board of Revenue Pakistan

**Live Demo:** [Explore the dataset online](https://old.hashirsafdar.com/pakistan-taxpayer/)

**Interactive Queries:** [Run SQL queries in your browser](https://old.hashirsafdar.com/pakistan-taxpayer/query.html) - Powered by DuckDB-WASM

## Dataset Overview

This dataset contains **2,847,352** taxpayer records from FBR's 2018 Income Tax Directory, extracted from a 229MB PDF with 35,445 pages.

### Companies
- **Records:** 44,609
- **Identifier:** 7-digit NTN (National Tax Number)
- **Fields:** Serial number, Taxpayer name, NTN, Tax paid (PKR)
- **Parquet file:** [companies.parquet](docs/companies.parquet) (~2MB)

### Association of Persons (AOP)
- **Records:** 64,336
- **Identifier:** 7-digit NTN (National Tax Number)
- **Fields:** Serial number, Taxpayer name, NTN, Tax paid (PKR)
- **Parquet file:** [aop.parquet](docs/aop.parquet) (~200KB)

### Individuals
- **Records:** 2,738,407
- **Identifier:** 13-digit CNIC (Computerized National Identity Card)
- **Fields:** Serial number, Taxpayer name, CNIC, Tax paid (PKR)
- **Parquet file:** [individuals.parquet](docs/individuals.parquet) (~46MB)

## Data Files

**Only Parquet files are included in this repository** due to GitHub's file size limits. The original PDF (229 MB) and CSV files (120 MB total) are not committed.

**Available Parquet files** (compressed, optimized for analytics):
- [companies.parquet](docs/companies.parquet) (1.2 MB) - 44,609 company records
- [aop.parquet](docs/aop.parquet) (1.5 MB) - 64,336 AOP records
- [individuals.parquet](docs/individuals.parquet) (45.8 MB) - 2,738,407 individual records

To generate CSV files from the original PDF, follow the extraction instructions in [EXTRACTION.md](EXTRACTION.md).

## Quick Start

### Download Parquet Files

Clone this repository to access the Parquet data files:
```bash
git clone https://github.com/hashirsafdar/pakistan-taxpayer.git
cd pakistan-taxpayer
```

Or download individual Parquet files directly:
- [companies.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/companies.parquet)
- [aop.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/aop.parquet)
- [individuals.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/individuals.parquet)

### Query Parquet Files

Using DuckDB:
```bash
duckdb -c "SELECT * FROM 'data/companies.parquet' LIMIT 10"
```

Using Python (pandas):
```python
import pandas as pd
df = pd.read_parquet('data/companies.parquet')
print(df.head())
```

## Data Schema

### Companies & AOP Tables
| Column | Type | Description |
|--------|------|-------------|
| `ntn` | TEXT | National Tax Number (Primary Key) |
| `sr` | INTEGER | Serial number from PDF |
| `name` | TEXT | Taxpayer name |
| `tax_paid` | REAL | Tax paid in PKR |

### Individuals Table
| Column | Type | Description |
|--------|------|-------------|
| `cnic` | TEXT | CNIC (Primary Key) |
| `sr` | INTEGER | Serial number from PDF |
| `name` | TEXT | Taxpayer name |
| `tax_paid` | REAL | Tax paid in PKR |

## Statistics

Total taxpayers by category:
- Companies: 44,609
- AOP: 64,336
- Individuals: 2,738,407
- **Total: 2,847,352**

## Technical Documentation

For details on how the data was extracted and processed, see [EXTRACTION.md](EXTRACTION.md).

## License

The original data is published by the Federal Board of Revenue Pakistan and is considered public information.

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/hashirsafdar/pakistan-taxpayer).
