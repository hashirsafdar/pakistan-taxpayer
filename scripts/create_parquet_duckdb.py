#!/usr/bin/env python3
"""
Create Parquet files from CSV data using DuckDB (much faster than pandas).
Parquet is a columnar format with much better compression than CSV.
"""

import duckdb


def csv_to_parquet_duckdb(csv_file, parquet_file):
    """Convert CSV to Parquet using DuckDB (fast, streaming)."""
    print(f"Converting {csv_file} to {parquet_file}...")

    con = duckdb.connect()
    con.execute(f"""
        COPY (SELECT * FROM read_csv_auto('{csv_file}'))
        TO '{parquet_file}' (FORMAT PARQUET, COMPRESSION SNAPPY)
    """)

    count = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{csv_file}')").fetchone()[0]
    print(f"  Done! {count:,} records")
    con.close()


def main():
    csv_to_parquet_duckdb('data/companies.csv', 'data/companies.parquet')
    csv_to_parquet_duckdb('data/aop.csv', 'data/aop.parquet')
    csv_to_parquet_duckdb('data/individuals.csv', 'data/individuals.parquet')

    import os
    print("\nFile sizes:")
    for csv, parquet in [('data/companies.csv', 'data/companies.parquet'),
                         ('data/aop.csv', 'data/aop.parquet'),
                         ('data/individuals.csv', 'data/individuals.parquet')]:
        if os.path.exists(csv) and os.path.exists(parquet):
            csv_size = os.path.getsize(csv) / (1024 * 1024)
            parquet_size = os.path.getsize(parquet) / (1024 * 1024)
            compression = (1 - parquet_size / csv_size) * 100
            print(f"  {csv}: {csv_size:.1f} MB → {parquet}: {parquet_size:.1f} MB ({compression:.1f}% smaller)")


if __name__ == '__main__':
    main()
