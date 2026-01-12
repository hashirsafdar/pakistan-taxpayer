# Pakistan Taxpayer Directory

Extracted and processed taxpayer data from the Federal Board of Revenue (FBR) Pakistan's Income Tax Directory for **6 years (2013-2018)**.

**Data Source:** [FBR Income Tax Directory](https://fbr.gov.pk/Categ/income-tax-directory/742) - Published by Federal Board of Revenue Pakistan

**Live Demo:** [Explore the dataset online](https://old.hashirsafdar.com/pakistan-taxpayer/)

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

**Only Parquet files are included in this repository** due to GitHub's file size limits. The original PDFs and CSV files are not committed.

All data files are organized by year in `docs/data/YEAR/` directories:

```
docs/data/
├── 2013/
│   ├── companies.parquet (0.5 MB)
│   ├── aop.parquet (0.8 MB)
│   └── individuals.parquet (10.3 MB)
├── 2014/
│   ├── companies.parquet (0.6 MB)
│   ├── aop.parquet (0.9 MB)
│   └── individuals.parquet (13.2 MB)
├── 2015/
│   ├── companies.parquet (0.7 MB)
│   ├── aop.parquet (1.0 MB)
│   └── individuals.parquet (10.3 MB)
├── 2016/
│   ├── companies.parquet (0.8 MB)
│   ├── aop.parquet (1.0 MB)
│   └── individuals.parquet (19.5 MB)
├── 2017/
│   ├── companies.parquet (1.0 MB)
│   ├── aop.parquet (1.2 MB)
│   └── individuals.parquet (29.4 MB)
└── 2018/
    ├── companies.parquet (1.2 MB)
    ├── aop.parquet (1.5 MB)
    └── individuals.parquet (55.2 MB)
```

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

# Query across multiple years
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

## Statistics

### Total Across All Years (2013-2018)
- **Companies:** 188,839 records
- **AOP:** 292,485 records
- **Individuals:** 7,767,625 records
- **Grand Total:** 8,248,949 taxpayer records

### Year-by-Year Breakdown
| Year | Companies | AOP | Individuals | Total |
|------|-----------|-----|-------------|-------|
| 2018 | 44,609 | 64,336 | 2,743,396 | 2,852,341 |
| 2017 | 37,127 | 53,811 | 1,680,396 | 1,771,334 |
| 2016 | 31,361 | 48,364 | 1,136,880 | 1,216,605 |
| 2015 | 28,097 | 44,600 | 691,259 | 763,956 |
| 2014 | 24,186 | 40,764 | 788,630 | 853,580 |
| 2013 | 23,459 | 40,610 | 727,064 | 791,133 |

## Technical Documentation

For details on how the data was extracted and processed, see [EXTRACTION.md](EXTRACTION.md).

## License

The original data is published by the Federal Board of Revenue Pakistan and is considered public information.

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/hashirsafdar/pakistan-taxpayer).
