#!/usr/bin/env python3
"""
Create SQLite database from CSV files.
Uses sqlite3 CLI's .import command for maximum performance.
"""

import os
import subprocess
import sys
from pathlib import Path


def create_database():
    """Create database using sqlite3 CLI for fast CSV import."""
    db_path = "data/taxpayers.db"

    print(f"Creating database: {db_path}")

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    # SQL commands to execute
    sql_commands = """
-- Create schema
CREATE TABLE companies (
    ntn TEXT PRIMARY KEY,
    sr INTEGER,
    name TEXT NOT NULL,
    tax_paid REAL
);

CREATE TABLE aop (
    ntn TEXT PRIMARY KEY,
    sr INTEGER,
    name TEXT NOT NULL,
    tax_paid REAL
);

CREATE TABLE individuals (
    sr INTEGER,
    name TEXT NOT NULL,
    cnic TEXT PRIMARY KEY,
    tax_paid REAL
);

-- Import data (uses fast C implementation)
.mode csv
.import --skip 1 data/companies.csv companies
.import --skip 1 data/aop.csv aop
.import --skip 1 data/individuals.csv individuals

-- Create views
CREATE VIEW top_companies AS
SELECT name, ntn, tax_paid
FROM companies
WHERE tax_paid > 0
ORDER BY tax_paid DESC
LIMIT 100;

CREATE VIEW top_aop AS
SELECT name, ntn, tax_paid
FROM aop
WHERE tax_paid > 0
ORDER BY tax_paid DESC
LIMIT 100;

CREATE VIEW top_individuals AS
SELECT name, cnic, tax_paid
FROM individuals
WHERE tax_paid > 0
ORDER BY tax_paid DESC
LIMIT 100;

-- Stats
SELECT 'Companies: ' || COUNT(*) || ' records' FROM companies;
SELECT 'AOP: ' || COUNT(*) || ' records' FROM aop;
SELECT 'Individuals: ' || COUNT(*) || ' records' FROM individuals;
"""

    # Execute via sqlite3 CLI
    result = subprocess.run(
        ['sqlite3', db_path],
        input=sql_commands,
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print(f"Error creating database: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Print stats output
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if line:
                print(line)

    print(f"\nDatabase created successfully: {db_path}")


if __name__ == '__main__':
    create_database()
