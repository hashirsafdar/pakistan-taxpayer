#!/usr/bin/env python3
"""
Create Parquet files from CSV data (requires pandas and pyarrow).
Parquet is a columnar format with much better compression than CSV.
"""

import sys

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed")
    print("Install with: pip install pandas pyarrow")
    sys.exit(1)

try:
    import pyarrow
except ImportError:
    print("Error: pyarrow not installed")
    print("Install with: pip install pyarrow")
    sys.exit(1)


def csv_to_parquet(csv_file, parquet_file):
    """Convert CSV to Parquet with compression."""
    print(f"Converting {csv_file} to {parquet_file}...")
    df = pd.read_csv(csv_file)
    df.to_parquet(
        parquet_file,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    print(f"  Done! {len(df):,} records")


def main():
    csv_to_parquet('companies.csv', 'companies.parquet')
    csv_to_parquet('individuals.csv', 'individuals.parquet')

    import os
    print("\nFile sizes:")
    for f in ['companies.csv', 'companies.parquet', 'individuals.csv', 'individuals.parquet']:
        if os.path.exists(f):
            size = os.path.getsize(f) / (1024 * 1024)
            print(f"  {f}: {size:.1f} MB")


if __name__ == '__main__':
    main()
