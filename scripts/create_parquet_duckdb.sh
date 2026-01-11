#!/bin/bash
set -euo pipefail

YEAR="${1:-2018}"
uv run --with duckdb "$(dirname "$0")/create_parquet_python.py" "$YEAR"
