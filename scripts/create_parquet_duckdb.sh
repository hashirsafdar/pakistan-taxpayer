#!/bin/bash
set -euo pipefail

echo "Creating Parquet files from CSV using DuckDB..."

# Function to convert CSV to Parquet
csv_to_parquet() {
    local csv_file=$1
    local parquet_file=$2

    echo "Converting $csv_file to $parquet_file..."

    duckdb :memory: <<EOF
COPY (SELECT * FROM read_csv_auto('$csv_file'))
TO '$parquet_file' (FORMAT PARQUET, COMPRESSION SNAPPY);

SELECT 'Done! ' || COUNT(*) || ' records' FROM read_csv_auto('$csv_file');
EOF
}

# Convert all files
csv_to_parquet "data/companies.csv" "data/companies.parquet"
csv_to_parquet "data/aop.csv" "data/aop.parquet"
csv_to_parquet "data/individuals.csv" "data/individuals.parquet"

# Show file sizes
echo ""
echo "File sizes:"
for csv_file in data/companies.csv data/aop.csv data/individuals.csv; do
    parquet_file="${csv_file%.csv}.parquet"
    if [ -f "$csv_file" ] && [ -f "$parquet_file" ]; then
        csv_size=$(stat -f%z "$csv_file" 2>/dev/null || stat -c%s "$csv_file")
        parquet_size=$(stat -f%z "$parquet_file" 2>/dev/null || stat -c%s "$parquet_file")
        csv_mb=$(echo "scale=1; $csv_size / 1024 / 1024" | bc)
        parquet_mb=$(echo "scale=1; $parquet_size / 1024 / 1024" | bc)
        compression=$(echo "scale=1; (1 - $parquet_size / $csv_size) * 100" | bc)
        echo "  $csv_file: ${csv_mb} MB → $parquet_file: ${parquet_mb} MB (${compression}% smaller)"
    fi
done

echo ""
echo "Parquet files created successfully!"
