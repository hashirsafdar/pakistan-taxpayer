#!/usr/bin/env python3
"""
Generate JSON data files for the web interface.
"""

import json
import sqlite3


def generate_top_taxpayers(conn, limit=1000):
    """Generate top taxpayers JSON."""
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, registration_no, tax_paid, 'company' as type
        FROM companies
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT ?
    ''', (limit // 2,))
    top_companies = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in cursor.fetchall()
    ]

    cursor.execute('''
        SELECT name, registration_no, tax_paid, 'individual' as type
        FROM individuals
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT ?
    ''', (limit // 2,))
    top_individuals = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in cursor.fetchall()
    ]

    top_all = sorted(
        top_companies + top_individuals,
        key=lambda x: x['tax'],
        reverse=True
    )[:limit]

    return {
        'top_companies': top_companies[:100],
        'top_individuals': top_individuals[:100],
        'top_all': top_all[:100]
    }


def generate_statistics(conn):
    """Generate statistics JSON."""
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM companies WHERE tax_paid > 0')
    comp_stats = cursor.fetchone()

    cursor.execute('SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM individuals WHERE tax_paid > 0')
    ind_stats = cursor.fetchone()

    return {
        'companies': {
            'total': comp_stats[0],
            'total_tax': comp_stats[1],
            'avg_tax': comp_stats[2],
            'max_tax': comp_stats[3]
        },
        'individuals': {
            'total': ind_stats[0],
            'total_tax': ind_stats[1],
            'avg_tax': ind_stats[2],
            'max_tax': ind_stats[3]
        }
    }


def main():
    conn = sqlite3.connect('taxpayers.db')

    print("Generating statistics...")
    stats = generate_statistics(conn)
    with open('docs/data/statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("  Written: docs/data/statistics.json")

    print("Generating top taxpayers...")
    top = generate_top_taxpayers(conn, 1000)
    with open('docs/data/top_taxpayers.json', 'w') as f:
        json.dump(top, f, indent=2)
    print("  Written: docs/data/top_taxpayers.json")

    conn.close()
    print("\nWeb data generation complete!")


if __name__ == '__main__':
    import os
    os.makedirs('docs/data', exist_ok=True)
    main()
