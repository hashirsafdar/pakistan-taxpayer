# Pakistan Taxpayer Directory

Extracted and processed taxpayer data from the Federal Board of Revenue (FBR) Pakistan's PDF Income Tax Directory for **6 years (2013-2018)**.


**Interactive Queries:** [Run SQL queries in your browser](https://old.hashirsafdar.com/pakistan-taxpayer/query.html) - Powered by DuckDB-WASM

## Dataset Overview

**Total Dataset: 8.2M+ taxpayer records** across 6 years (2013-2018)

| Year | Companies | AOP | Individuals | Total | Format |
|------|-----------|-----|-------------|-------|--------|
| 2018 | 44,609 | 64,336 | 2,743,396 | 2,852,341 | Serial + 7-digit NTN/variable CNIC |
| 2017 | 37,127 | 53,811 | 1,680,396 | 1,771,334 | Serial + 7-digit NTN/variable CNIC |
| 2016 | 31,361 | 48,364 | 1,136,880 | 1,216,605 | 8-digit NTN/variable CNIC |
| 2015 | 28,097 | 44,600 | 691,259 | 763,956 | 8-digit NTN/variable CNIC |
| 2014 | 24,186 | 40,764 | 788,630 | 853,580 | 8-digit NTN/variable CNIC |
| 2013 | 23,459 | 40,610 | 727,064 | 791,133 | 8-digit NTN (individuals use NTN) |
| **Total** | **188,839** | **292,485** | **7,767,625** | **8,248,949** | |

## Data Files

To save you from working with a ten-thousand page PDF, parquet data files are shared:

```
docs/data/
├── all.parquet
├── YEAR/
│   ├── companies.parquet
│   ├── aop.parquet
│   └── individuals.parquet
```

The original PDFs are not committed due to size, but the scripts expect them to be in the respective year folder for extraction.

To generate CSV files from the original PDFs, follow the extraction instructions in [EXTRACTION.md](EXTRACTION.md).

## Quick Start

### Download Parquet Files

Clone this repository to access the Parquet data files:
```bash
git clone https://github.com/hashirsafdar/pakistan-taxpayer.git
cd pakistan-taxpayer
```

### Query Parquet Files

Using DuckDB:
```bash
# Query 2018 companies
duckdb -c "SELECT * FROM 'docs/data/2018/companies.parquet' LIMIT 10"

# Search by NTN (first 7 digits only)
duckdb -c "
  SELECT * FROM 'docs/data/2018/companies.parquet'
  WHERE LEFT(CAST(ntn_7 AS VARCHAR), 7) = '0787223'
"

# Query across multiple years (matches entities by first 7 NTN digits)
duckdb -c "
  SELECT '2017' as year, * FROM 'docs/data/2017/individuals.parquet'
  UNION ALL
  SELECT '2018' as year, * FROM 'docs/data/2018/individuals.parquet'
  ORDER BY tax_paid DESC LIMIT 100
"
```

Using Python (pandas):
```python
import pandas as pd

# Read single year
df_2018 = pd.read_parquet('docs/data/2018/companies.parquet')
print(df_2018.head())

# Combine multiple years
import glob
dfs = []
for file in glob.glob('docs/data/*/individuals.parquet'):
    year = file.split('/')[2]
    df = pd.read_parquet(file)
    df['year'] = year
    dfs.append(df)
combined = pd.concat(dfs)
```

## Technical Documentation

For details on how the data was extracted and processed, see [EXTRACTION.md](EXTRACTION.md).

## License

The original data is published by the Federal Board of Revenue Pakistan and is considered public information.
[FBR Income Tax Directory](https://fbr.gov.pk/Categ/income-tax-directory/742)
