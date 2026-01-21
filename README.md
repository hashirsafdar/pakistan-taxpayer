# Pakistan Taxpayer Directory

Extracted and processed taxpayer data from the Federal Board of Revenue (FBR) Pakistan's PDF Income Tax Directory for **6 years (2013-2018)**.

[Explore the top 1000 taxpayers across all this data here](https://github.hashirsafdar.com/pakistan-taxpayer/)

## Dataset Overview

FBR shares all this data as anyone would: giant 10000+ page PDFs exported from word.

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

Data has been transformed into a file for each category and year. There is also an `all.parquet` that combines all of this data together, and is conveniently smaller than the smallest PDF file.

In the repo, the parquet data files are shared as such:

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

**In-browser Queries:** [Run SQL queries in your browser](https://github.hashirsafdar.com/pakistan-taxpayer/query.html) - Use DuckDB-WASM to query parquet files in your browser

See query examples in [EXTRACTION.md](EXTRACTION.md).

## License

The original data is published by the Federal Board of Revenue Pakistan and is considered public information.
[FBR Income Tax Directory](https://fbr.gov.pk/Categ/income-tax-directory/742)

Everything else is shared under the [MIT license](LICENSE).
