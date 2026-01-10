#!/usr/bin/env -S uvx --with duckdb python3
"""
Generate JSON data files for the web interface from Parquet files.
"""

import json
import duckdb


def generate_top_taxpayers(conn, limit=1000):
    """Generate top taxpayers JSON."""

    top_companies = conn.execute('''
        SELECT name, ntn, tax_paid, 'company' as type
        FROM 'data/companies.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT ?
    ''', (limit // 3,)).fetchall()
    top_companies = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in top_companies
    ]

    top_aop = conn.execute('''
        SELECT name, ntn, tax_paid, 'aop' as type
        FROM 'data/aop.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT ?
    ''', (limit // 3,)).fetchall()
    top_aop = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in top_aop
    ]

    top_individuals = conn.execute('''
        SELECT name, cnic, tax_paid, 'individual' as type
        FROM 'data/individuals.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT ?
    ''', (limit // 3,)).fetchall()
    top_individuals = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in top_individuals
    ]

    top_all = sorted(
        top_companies + top_aop + top_individuals,
        key=lambda x: x['tax'],
        reverse=True
    )[:limit]

    return {
        'top_companies': top_companies[:100],
        'top_aop': top_aop[:100],
        'top_individuals': top_individuals[:100],
        'top_all': top_all[:100]
    }


def generate_statistics(conn):
    """Generate statistics JSON."""

    comp_stats = conn.execute(
        "SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'data/companies.parquet' WHERE tax_paid > 0"
    ).fetchone()

    aop_stats = conn.execute(
        "SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'data/aop.parquet' WHERE tax_paid > 0"
    ).fetchone()

    ind_stats = conn.execute(
        "SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'data/individuals.parquet' WHERE tax_paid > 0"
    ).fetchone()

    return {
        'companies': {
            'total': comp_stats[0],
            'total_tax': comp_stats[1],
            'avg_tax': comp_stats[2],
            'max_tax': comp_stats[3]
        },
        'aop': {
            'total': aop_stats[0],
            'total_tax': aop_stats[1],
            'avg_tax': aop_stats[2],
            'max_tax': aop_stats[3]
        },
        'individuals': {
            'total': ind_stats[0],
            'total_tax': ind_stats[1],
            'avg_tax': ind_stats[2],
            'max_tax': ind_stats[3]
        }
    }


def main():
    conn = duckdb.connect()

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
