#!/bin/bash
set -euo pipefail

DB="data/taxpayers.db"

echo "Creating database: $DB"
rm -f "$DB"

sqlite3 "$DB" <<EOF
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

-- Import data (much faster than Python)
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
EOF

echo "Database created successfully: $DB"
