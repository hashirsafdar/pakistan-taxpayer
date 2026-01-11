#!/usr/bin/env python3
import sys
import os
import duckdb
from pathlib import Path

year = sys.argv[1] if len(sys.argv) > 1 else "2018"
year_suffix = f"_{year}"

print(f"Creating Parquet files from CSV using DuckDB (Year: {year})...")

files_to_convert = [
    ("companies", f"data/companies{year_suffix}.csv", f"data/companies{year_suffix}.parquet"),
    ("aop", f"data/aop{year_suffix}.csv", f"data/aop{year_suffix}.parquet"),
    ("individuals", f"data/individuals{year_suffix}.csv", f"data/individuals{year_suffix}.parquet"),
]

conn = duckdb.connect(":memory:")

for name, csv_file, parquet_file in files_to_convert:
    print(f"Converting {csv_file} to {parquet_file}...")

    # Read CSV and write to Parquet
    df = conn.read_csv(csv_file)
    record_count = len(df)
    df.write_parquet(parquet_file)

    print(f"  Done! {record_count} records")

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
        print(f"  {csv_file}: {csv_mb:.1f} MB → {parquet_file}: {parquet_mb:.1f} MB ({compression:.0f}% smaller)")

print("\nParquet files created successfully!")
