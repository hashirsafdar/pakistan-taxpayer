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

    # Determine sort column and padding based on entity type and year
    # Pad IDs to fixed length for proper string sorting (critical for row group pruning)
    if entity_type == 'individuals':
        if year == '2013':
            id_col = 'ntn_8'
            pad_length = 8
        else:
            id_col = 'cnic'
            pad_length = 13
    else:  # companies, aop
        if int(year) <= 2016:
            id_col = 'ntn_8'
            pad_length = 8
        else:
            id_col = 'ntn_7'
            pad_length = 7

    # Build SELECT clause that pads the ID column
    # Schema by year:
    # 2017-2018: sr, name, ntn_7/cnic, tax_paid (has serial numbers)
    # 2014-2016: name, ntn_8/cnic, tax_paid (no serial)
    # 2013: name, ntn_8, tax_paid (all types)
    has_sr = int(year) >= 2017

    if has_sr:
        select_clause = f"sr, name, LPAD(CAST(COALESCE({id_col}, '') AS VARCHAR), {pad_length}, '0') as {id_col}, tax_paid"
    else:
        select_clause = f"name, LPAD(CAST(COALESCE({id_col}, '') AS VARCHAR), {pad_length}, '0') as {id_col}, tax_paid"

    # Sort data before writing to create non-overlapping row group statistics
    # This enables DuckDB-WASM to skip row groups via HTTP range requests
    # Use small row groups (5000 rows) to ensure even small files get multiple row groups
    conn.execute(f'''
        COPY (
            SELECT {select_clause}
            FROM read_csv('{csv_file}', null_padding=true)
            ORDER BY {id_col}
        ) TO '{parquet_file}' (FORMAT 'parquet', COMPRESSION 'gzip', ROW_GROUP_SIZE 5000)
    ''')

    # Get record count for reporting
    record_count = conn.execute(f"SELECT COUNT(*) FROM read_csv('{csv_file}', null_padding=true)").fetchone()[0]

    print(f"  Done! {record_count} records (sorted by {id_col}, padded to {pad_length} digits)")

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
