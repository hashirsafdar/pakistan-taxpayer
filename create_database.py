#!/usr/bin/env python3
"""
Create SQLite database and load taxpayer data from CSV files.
"""

import sqlite3
import csv
from pathlib import Path


def create_schema(conn):
    """Create database schema with primary keys on NTN/CNIC."""
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            ntn TEXT PRIMARY KEY,
            sr INTEGER,
            name TEXT NOT NULL,
            tax_paid REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aop (
            ntn TEXT PRIMARY KEY,
            sr INTEGER,
            name TEXT NOT NULL,
            tax_paid REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS individuals (
            cnic TEXT PRIMARY KEY,
            sr INTEGER,
            name TEXT NOT NULL,
            tax_paid REAL
        )
    ''')

    conn.commit()
    print("Database schema created successfully")


def load_csv_to_table(conn, csv_file, table_name):
    """Load CSV data into specified table."""
    if not Path(csv_file).exists():
        print(f"Warning: {csv_file} not found, skipping...")
        return 0

    cursor = conn.cursor()
    count = 0

    # Determine the ID column name based on table
    id_col = 'cnic' if table_name == 'individuals' else 'ntn'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []

        for row in reader:
            rows.append((
                row[id_col],
                int(row['sr']),
                row['name'],
                float(row['tax_paid'])
            ))
            count += 1

            if len(rows) >= 1000:
                cursor.executemany(
                    f'INSERT OR IGNORE INTO {table_name} ({id_col}, sr, name, tax_paid) VALUES (?, ?, ?, ?)',
                    rows
                )
                rows = []
                if count % 10000 == 0:
                    print(f"  Loaded {count:,} records...")

        if rows:
            cursor.executemany(
                f'INSERT OR IGNORE INTO {table_name} ({id_col}, sr, name, tax_paid) VALUES (?, ?, ?, ?)',
                rows
            )

    conn.commit()
    print(f"Loaded {count:,} records into {table_name}")
    return count


def create_query_helpers(conn):
    """Create views and helper queries."""
    cursor = conn.cursor()

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS top_companies AS
        SELECT name, ntn, tax_paid
        FROM companies
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT 100
    ''')

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS top_aop AS
        SELECT name, ntn, tax_paid
        FROM aop
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT 100
    ''')

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS top_individuals AS
        SELECT name, cnic, tax_paid
        FROM individuals
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT 100
    ''')

    conn.commit()
    print("Helper views created")


def print_stats(conn):
    """Print database statistics."""
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM companies')
    comp_stats = cursor.fetchone()

    cursor.execute('SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM aop')
    aop_stats = cursor.fetchone()

    cursor.execute('SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM individuals')
    ind_stats = cursor.fetchone()

    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    print(f"\nCompanies:")
    print(f"  Total records: {comp_stats[0]:,}")
    print(f"  Total tax paid: {comp_stats[1]:,.2f}" if comp_stats[1] else "  Total tax paid: 0")
    print(f"  Average tax: {comp_stats[2]:,.2f}" if comp_stats[2] else "  Average tax: 0")
    print(f"  Maximum tax: {comp_stats[3]:,.2f}" if comp_stats[3] else "  Maximum tax: 0")

    print(f"\nAssociation of Persons (AOP):")
    print(f"  Total records: {aop_stats[0]:,}")
    print(f"  Total tax paid: {aop_stats[1]:,.2f}" if aop_stats[1] else "  Total tax paid: 0")
    print(f"  Average tax: {aop_stats[2]:,.2f}" if aop_stats[2] else "  Average tax: 0")
    print(f"  Maximum tax: {aop_stats[3]:,.2f}" if aop_stats[3] else "  Maximum tax: 0")

    print(f"\nIndividuals:")
    print(f"  Total records: {ind_stats[0]:,}")
    print(f"  Total tax paid: {ind_stats[1]:,.2f}" if ind_stats[1] else "  Total tax paid: 0")
    print(f"  Average tax: {ind_stats[2]:,.2f}" if ind_stats[2] else "  Average tax: 0")
    print(f"  Maximum tax: {ind_stats[3]:,.2f}" if ind_stats[3] else "  Maximum tax: 0")
    print("=" * 80)


def main():
    db_path = 'taxpayers.db'

    print(f"Creating database: {db_path}")
    conn = sqlite3.connect(db_path)

    create_schema(conn)

    print("\nLoading companies from CSV...")
    load_csv_to_table(conn, 'companies.csv', 'companies')

    print("\nLoading Association of Persons (AOP) from CSV...")
    load_csv_to_table(conn, 'aop.csv', 'aop')

    print("\nLoading individuals from CSV...")
    load_csv_to_table(conn, 'individuals.csv', 'individuals')

    create_query_helpers(conn)

    print_stats(conn)

    conn.close()
    print(f"\nDatabase created successfully: {db_path}")


if __name__ == '__main__':
    main()
