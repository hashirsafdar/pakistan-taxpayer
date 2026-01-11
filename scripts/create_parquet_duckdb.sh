#!/bin/bash
set -euo pipefail

YEAR="${1:-2018}"
python3 "$(dirname "$0")/create_parquet_python.py" "$YEAR"
