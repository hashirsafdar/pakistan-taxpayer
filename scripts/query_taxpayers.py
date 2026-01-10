#!/usr/bin/env python3
"""
Query taxpayer database.
"""

import sqlite3
import sys


def search_by_name(conn, name, entity_type='all', limit=20):
    """Search taxpayers by name."""
    cursor = conn.cursor()
    name_pattern = f"%{name}%"

    results = []

    if entity_type in ['all', 'company']:
        cursor.execute('''
            SELECT 'Company' as type, name, ntn, tax_paid
            FROM companies
            WHERE name LIKE ?
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (name_pattern, limit))
        results.extend(cursor.fetchall())

    if entity_type in ['all', 'individual']:
        cursor.execute('''
            SELECT 'Individual' as type, name, cnic, tax_paid
            FROM individuals
            WHERE name LIKE ?
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (name_pattern, limit))
        results.extend(cursor.fetchall())

    return results


def search_by_regno(conn, regno):
    """Search by NTN or CNIC."""
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 'Company' as type, name, ntn, tax_paid
        FROM companies
        WHERE ntn = ?
    ''', (regno,))
    result = cursor.fetchone()

    if not result:
        cursor.execute('''
            SELECT 'Individual' as type, name, cnic, tax_paid
            FROM individuals
            WHERE cnic = ?
        ''', (regno,))
        result = cursor.fetchone()

    return [result] if result else []


def get_top_taxpayers(conn, entity_type='all', limit=20):
    """Get top taxpayers by tax paid."""
    cursor = conn.cursor()
    results = []

    if entity_type in ['all', 'company']:
        cursor.execute('''
            SELECT 'Company' as type, name, ntn, tax_paid
            FROM companies
            WHERE tax_paid > 0
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (limit,))
        results.extend(cursor.fetchall())

    if entity_type in ['all', 'individual']:
        cursor.execute('''
            SELECT 'Individual' as type, name, cnic, tax_paid
            FROM individuals
            WHERE tax_paid > 0
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (limit,))
        results.extend(cursor.fetchall())

    if entity_type == 'all':
        results.sort(key=lambda x: x[3], reverse=True)
        results = results[:limit]

    return results


def get_tax_range(conn, min_tax, max_tax, entity_type='all', limit=100):
    """Get taxpayers within a tax range."""
    cursor = conn.cursor()
    results = []

    if entity_type in ['all', 'company']:
        cursor.execute('''
            SELECT 'Company' as type, name, ntn, tax_paid
            FROM companies
            WHERE tax_paid BETWEEN ? AND ?
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (min_tax, max_tax, limit))
        results.extend(cursor.fetchall())

    if entity_type in ['all', 'individual']:
        cursor.execute('''
            SELECT 'Individual' as type, name, cnic, tax_paid
            FROM individuals
            WHERE tax_paid BETWEEN ? AND ?
            ORDER BY tax_paid DESC
            LIMIT ?
        ''', (min_tax, max_tax, limit))
        results.extend(cursor.fetchall())

    return results


def print_results(results):
    """Print query results in a formatted table."""
    if not results:
        print("No results found.")
        return

    print("\n" + "=" * 120)
    print(f"{'Type':<12} {'Name':<60} {'NTN/CNIC':<15} {'Tax Paid':>15}")
    print("=" * 120)

    for row in results:
        type_val, name, regno, tax = row
        name = name[:58] if len(name) > 58 else name
        print(f"{type_val:<12} {name:<60} {regno:<15} {tax:>15,.2f}")

    print("=" * 120)
    print(f"Total results: {len(results)}\n")


def main():
    db_path = 'data/taxpayers.db'

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error: Could not connect to database: {e}")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_taxpayers.py name <search_term> [company|individual|all] [limit]")
        print("  python query_taxpayers.py regno <registration_number>")
        print("  python query_taxpayers.py top [company|individual|all] [limit]")
        print("  python query_taxpayers.py range <min_tax> <max_tax> [company|individual|all] [limit]")
        print("\nExamples:")
        print("  python query_taxpayers.py name 'abbott' company 10")
        print("  python query_taxpayers.py regno 1347561")
        print("  python query_taxpayers.py top company 20")
        print("  python query_taxpayers.py range 1000000 10000000 all 50")
        conn.close()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'name':
        if len(sys.argv) < 3:
            print("Error: Please provide search term")
            sys.exit(1)
        name = sys.argv[2]
        entity_type = sys.argv[3] if len(sys.argv) > 3 else 'all'
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        results = search_by_name(conn, name, entity_type, limit)
        print(f"\nSearching for: {name} (Type: {entity_type})")
        print_results(results)

    elif command == 'regno':
        if len(sys.argv) < 3:
            print("Error: Please provide registration number")
            sys.exit(1)
        regno = sys.argv[2]
        results = search_by_regno(conn, regno)
        print(f"\nSearching for registration number: {regno}")
        print_results(results)

    elif command == 'top':
        entity_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        results = get_top_taxpayers(conn, entity_type, limit)
        print(f"\nTop {limit} taxpayers (Type: {entity_type})")
        print_results(results)

    elif command == 'range':
        if len(sys.argv) < 4:
            print("Error: Please provide min and max tax amounts")
            sys.exit(1)
        min_tax = float(sys.argv[2])
        max_tax = float(sys.argv[3])
        entity_type = sys.argv[4] if len(sys.argv) > 4 else 'all'
        limit = int(sys.argv[5]) if len(sys.argv) > 5 else 100
        results = get_tax_range(conn, min_tax, max_tax, entity_type, limit)
        print(f"\nTaxpayers with tax paid between {min_tax:,.2f} and {max_tax:,.2f} (Type: {entity_type})")
        print_results(results)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)

    conn.close()


if __name__ == '__main__':
    main()
