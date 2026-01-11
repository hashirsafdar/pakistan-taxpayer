# Pakistan Taxpayer Directory

Extracted and processed taxpayer data from the Federal Board of Revenue (FBR) Pakistan's Income Tax Directory for multiple years (2017, 2018).

**Data Source:** [FBR Income Tax Directory](https://fbr.gov.pk/Categ/income-tax-directory/742) - Published by Federal Board of Revenue Pakistan

**Live Demo:** [Explore the dataset online](https://old.hashirsafdar.com/pakistan-taxpayer/)

**Interactive Queries:** [Run SQL queries in your browser](https://old.hashirsafdar.com/pakistan-taxpayer/query.html) - Powered by DuckDB-WASM

## Dataset Overview

### 2018 Data
**Total: 2,847,352** taxpayer records from FBR's 2018 Income Tax Directory, extracted from a 229MB PDF with 35,445 pages.

#### Companies (2018)
- **Records:** 44,609
- **Identifier:** 7-digit NTN (National Tax Number)
- **Fields:** Serial number, Taxpayer name, NTN, Tax paid (PKR)
- **Parquet file:** [companies_2018.parquet](docs/companies_2018.parquet) (~1.3MB)

#### Association of Persons (AOP) (2018)
- **Records:** 64,336
- **Identifier:** 7-digit NTN (National Tax Number)
- **Fields:** Serial number, Taxpayer name, NTN, Tax paid (PKR)
- **Parquet file:** [aop_2018.parquet](docs/aop_2018.parquet) (~1.6MB)

#### Individuals (2018)
- **Records:** 2,738,407
- **Identifier:** 13-digit CNIC (Computerized National Identity Card)
- **Fields:** Serial number, Taxpayer name, CNIC, Tax paid (PKR)
- **Parquet file:** [individuals_2018.parquet](docs/individuals_2018.parquet) (~46MB)

### 2017 Data
**Total: 1,771,318** taxpayer records from FBR's 2017 Income Tax Directory, extracted from a 155MB PDF.

#### Companies (2017)
- **Records:** 40,080
- **Parquet file:** [companies_2017.parquet](docs/companies_2017.parquet) (~1.1MB)

#### Association of Persons (AOP) (2017)
- **Records:** 53,811
- **Parquet file:** [aop_2017.parquet](docs/aop_2017.parquet) (~1.3MB)

#### Individuals (2017)
- **Records:** 1,677,427
- **Parquet file:** [individuals_2017.parquet](docs/individuals_2017.parquet) (~30MB)

## Data Files

**Only Parquet files are included in this repository** due to GitHub's file size limits. The original PDFs and CSV files are not committed.

**Available Parquet files** (compressed, optimized for analytics):

**2018 Data:**
- [companies_2018.parquet](docs/companies_2018.parquet) (1.3 MB) - 44,609 company records
- [aop_2018.parquet](docs/aop_2018.parquet) (1.6 MB) - 64,336 AOP records
- [individuals_2018.parquet](docs/individuals_2018.parquet) (46 MB) - 2,738,407 individual records

**2017 Data:**
- [companies_2017.parquet](docs/companies_2017.parquet) (1.1 MB) - 40,080 company records
- [aop_2017.parquet](docs/aop_2017.parquet) (1.3 MB) - 53,811 AOP records
- [individuals_2017.parquet](docs/individuals_2017.parquet) (30 MB) - 1,677,427 individual records

To generate CSV files from the original PDF, follow the extraction instructions in [EXTRACTION.md](EXTRACTION.md).

## Quick Start

### Download Parquet Files

Clone this repository to access the Parquet data files:
```bash
git clone https://github.com/hashirsafdar/pakistan-taxpayer.git
cd pakistan-taxpayer
```

Or download individual Parquet files directly:

**2018 Files:**
- [companies_2018.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/companies_2018.parquet)
- [aop_2018.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/aop_2018.parquet)
- [individuals_2018.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/individuals_2018.parquet)

**2017 Files:**
- [companies_2017.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/companies_2017.parquet)
- [aop_2017.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/aop_2017.parquet)
- [individuals_2017.parquet](https://old.hashirsafdar.com/pakistan-taxpayer/individuals_2017.parquet)

### Query Parquet Files

Using DuckDB (2018):
```bash
duckdb -c "SELECT * FROM 'data/companies_2018.parquet' LIMIT 10"
```

Using DuckDB (2017):
```bash
duckdb -c "SELECT * FROM 'data/companies_2017.parquet' LIMIT 10"
```

Using Python (pandas) for 2018:
```python
import pandas as pd
df = pd.read_parquet('data/companies_2018.parquet')
print(df.head())
```

Using Python (pandas) for 2017:
```python
import pandas as pd
df = pd.read_parquet('data/companies_2017.parquet')
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

### 2018 Totals
- Companies: 44,609
- AOP: 64,336
- Individuals: 2,738,407
- **Total: 2,847,352**

### 2017 Totals
- Companies: 40,080
- AOP: 53,811
- Individuals: 1,677,427
- **Total: 1,771,318**

### Combined (2017-2018)
- Companies: 84,689
- AOP: 118,147
- Individuals: 4,415,834
- **Total: 4,618,670**

## Technical Documentation

For details on how the data was extracted and processed, see [EXTRACTION.md](EXTRACTION.md).

## License

The original data is published by the Federal Board of Revenue Pakistan and is considered public information.

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/hashirsafdar/pakistan-taxpayer).
