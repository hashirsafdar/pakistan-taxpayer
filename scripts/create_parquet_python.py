#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import duckdb

year = sys.argv[1] if len(sys.argv) > 1 else "2018"
year_suffix = f"_{year}"

print(f"Creating Parquet files from CSV using DuckDB (Year: {year})...")

files_to_convert = [
    ("companies", f"docs/data/{year}/companies.csv", f"docs/data/{year}/companies.parquet"),
    ("aop", f"docs/data/{year}/aop.csv", f"docs/data/{year}/aop.parquet"),
    ("individuals", f"docs/data/{year}/individuals.csv", f"docs/data/{year}/individuals.parquet"),
]

conn = duckdb.connect(":memory:")

for entity_type, csv_file, parquet_file in files_to_convert:
    print(f"Converting {csv_file} to {parquet_file}...")

    # Determine sort column based on entity type and year
    if entity_type == 'individuals':
        sort_col = 'ntn_8' if year == '2013' else 'cnic'
    else:  # companies, aop
        sort_col = 'ntn_8' if int(year) <= 2016 else 'ntn_7'

    # Sort data before writing to create non-overlapping row group statistics
    # This enables DuckDB-WASM to skip row groups via HTTP range requests
    conn.execute(f'''
        COPY (
            SELECT * FROM read_csv('{csv_file}', null_padding=true)
            ORDER BY {sort_col}
        ) TO '{parquet_file}' (FORMAT 'parquet', COMPRESSION 'gzip')
    ''')

    # Get record count for reporting
    record_count = conn.execute(f"SELECT COUNT(*) FROM read_csv('{csv_file}', null_padding=true)").fetchone()[0]

    print(f"  Done! {record_count} records (sorted by {sort_col})")

conn.close()

# Show file sizes
print("\nFile sizes:")
for name, csv_file, parquet_file in files_to_convert:
    if os.path.exists(csv_file) and os.path.exists(parquet_file):
        csv_size = os.path.getsize(csv_file)
        parquet_size = os.path.getsize(parquet_file)
        csv_mb = csv_size / 1024 / 1024
        parquet_mb = parquet_size / 1024 / 1024
        compression = (1 - parquet_size / csv_size) * 100
        print(
            f"  {csv_file}: {csv_mb:.1f} MB → {parquet_file}: {parquet_mb:.1f} MB ({compression:.0f}% smaller)"
        )

print("\nParquet files created successfully!")
