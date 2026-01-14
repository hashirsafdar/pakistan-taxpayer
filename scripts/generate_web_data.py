#!/usr/bin/env -S uvx --with duckdb python3
"""
Generate JSON data files for the web interface from Parquet files.
"""

import json
import duckdb
import os


def generate_top_taxpayers(conn, year, limit=1000):
    """Generate top taxpayers JSON for a specific year."""

    ntn_col_companies = 'ntn_8' if year <= 2016 else 'ntn_7'
    id_col_individuals = 'ntn_8' if year == 2013 else 'cnic'

    top_companies = conn.execute(f'''
        SELECT name, {ntn_col_companies}, tax_paid, 'company' as type
        FROM 'docs/data/{year}/companies.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT {limit // 3}
    ''').fetchall()
    top_companies = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in top_companies
    ]

    top_aop = conn.execute(f'''
        SELECT name, {ntn_col_companies}, tax_paid, 'aop' as type
        FROM 'docs/data/{year}/aop.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT {limit // 3}
    ''').fetchall()
    top_aop = [
        {
            'name': row[0],
            'regno': row[1],
            'tax': row[2],
            'type': row[3]
        }
        for row in top_aop
    ]

    top_individuals = conn.execute(f'''
        SELECT name, {id_col_individuals}, tax_paid, 'individual' as type
        FROM 'docs/data/{year}/individuals.parquet'
        WHERE tax_paid > 0
        ORDER BY tax_paid DESC
        LIMIT {limit // 3}
    ''').fetchall()
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


def generate_statistics(conn, year):
    """Generate statistics JSON for a specific year."""

    comp_stats = conn.execute(
        f"SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'docs/data/{year}/companies.parquet' WHERE tax_paid > 0"
    ).fetchone()

    aop_stats = conn.execute(
        f"SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'docs/data/{year}/aop.parquet' WHERE tax_paid > 0"
    ).fetchone()

    ind_stats = conn.execute(
        f"SELECT COUNT(*), SUM(tax_paid), AVG(tax_paid), MAX(tax_paid) FROM 'docs/data/{year}/individuals.parquet' WHERE tax_paid > 0"
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


def generate_top_taxpayers_across_years(conn, years):
    """Generate top 100 taxpayers across all years."""

    print("\nGenerating top taxpayers across all years...")

    companies_query = ' UNION ALL '.join([
        f"""
        SELECT
            LEFT(CAST({'ntn_8' if year <= 2016 else 'ntn_7'} AS VARCHAR), 7) as ntn7,
            {'ntn_8' if year <= 2016 else 'ntn_7'} as ntn,
            name,
            {year} as year,
            tax_paid
        FROM 'docs/data/{year}/companies.parquet'
        WHERE tax_paid > 0
        """ for year in years
    ])

    companies = conn.execute(f"""
        WITH all_years AS ({companies_query}),
        yearly_aggregated AS (
            SELECT
                ntn7,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn
            FROM all_years
            GROUP BY ntn7, year
        ),
        aggregated AS (
            SELECT
                ntn7,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn,
                SUM(year_tax) as total_tax,
                MAP_FROM_ENTRIES(LIST(ROW(year, year_tax) ORDER BY year)) as year_breakdown
            FROM yearly_aggregated
            GROUP BY ntn7
        )
        SELECT name, ntn, year_breakdown, total_tax
        FROM aggregated
        ORDER BY total_tax DESC
        LIMIT 100
    """).fetchall()

    companies_data = []
    for row in companies:
        breakdown = dict(row[2])
        companies_data.append({
            'name': row[0],
            'ntn': row[1],
            'years': {str(year): breakdown.get(year, 0) for year in years},
            'total': row[3]
        })

    aop_query = ' UNION ALL '.join([
        f"""
        SELECT
            LEFT(CAST({'ntn_8' if year <= 2016 else 'ntn_7'} AS VARCHAR), 7) as ntn7,
            {'ntn_8' if year <= 2016 else 'ntn_7'} as ntn,
            name,
            {year} as year,
            tax_paid
        FROM 'docs/data/{year}/aop.parquet'
        WHERE tax_paid > 0
        """ for year in years
    ])

    aop = conn.execute(f"""
        WITH all_years AS ({aop_query}),
        yearly_aggregated AS (
            SELECT
                ntn7,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn
            FROM all_years
            GROUP BY ntn7, year
        ),
        aggregated AS (
            SELECT
                ntn7,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn,
                SUM(year_tax) as total_tax,
                MAP_FROM_ENTRIES(LIST(ROW(year, year_tax) ORDER BY year)) as year_breakdown
            FROM yearly_aggregated
            GROUP BY ntn7
        )
        SELECT name, ntn, year_breakdown, total_tax
        FROM aggregated
        ORDER BY total_tax DESC
        LIMIT 100
    """).fetchall()

    aop_data = []
    for row in aop:
        breakdown = dict(row[2])
        aop_data.append({
            'name': row[0],
            'ntn': row[1],
            'years': {str(year): breakdown.get(year, 0) for year in years},
            'total': row[3]
        })

    individuals_parts = []
    for year in years:
        id_col = 'ntn_8' if year == 2013 else 'cnic'
        individuals_parts.append(f"""
            SELECT
                {id_col} as id,
                name,
                {year} as year,
                tax_paid
            FROM 'docs/data/{year}/individuals.parquet'
            WHERE tax_paid > 0
        """)

    individuals_query = ' UNION ALL '.join(individuals_parts)

    individuals = conn.execute(f"""
        WITH all_years AS ({individuals_query}),
        yearly_aggregated AS (
            SELECT
                id,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name
            FROM all_years
            GROUP BY id, year
        ),
        aggregated AS (
            SELECT
                id,
                FIRST(name ORDER BY year DESC) as name,
                SUM(year_tax) as total_tax,
                MAP_FROM_ENTRIES(LIST(ROW(year, year_tax) ORDER BY year)) as year_breakdown
            FROM yearly_aggregated
            GROUP BY id
        )
        SELECT name, id, year_breakdown, total_tax
        FROM aggregated
        ORDER BY total_tax DESC
        LIMIT 100
    """).fetchall()

    individuals_data = []
    for row in individuals:
        breakdown = dict(row[2])
        individuals_data.append({
            'name': row[0],
            'id': row[1],
            'years': {str(year): breakdown.get(year, 0) for year in years},
            'total': row[3]
        })

    return {
        'companies': companies_data,
        'aop': aop_data,
        'individuals': individuals_data
    }


def main():
    os.makedirs('docs/data/web', exist_ok=True)
    conn = duckdb.connect()

    years = [2013, 2014, 2015, 2016, 2017, 2018]

    for year in years:
        print(f"\nProcessing year {year}...")

        if not os.path.exists(f'docs/data/{year}/companies.parquet'):
            print(f"  Skipping {year} - data files not found")
            continue

        print(f"  Generating statistics for {year}...")
        stats = generate_statistics(conn, year)
        with open(f'docs/data/web/statistics_{year}.json', 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"    Written: docs/data/web/statistics_{year}.json")

        print(f"  Generating top taxpayers for {year}...")
        top = generate_top_taxpayers(conn, year, 1000)
        with open(f'docs/data/web/top_taxpayers_{year}.json', 'w') as f:
            json.dump(top, f, indent=2)
        print(f"    Written: docs/data/web/top_taxpayers_{year}.json")

    print("\nGenerating across-years top 100...")
    across_years = generate_top_taxpayers_across_years(conn, years)
    with open('docs/data/web/top_taxpayers_across_years.json', 'w') as f:
        json.dump(across_years, f, indent=2)
    print("  Written: docs/data/web/top_taxpayers_across_years.json")

    conn.close()
    print("\nWeb data generation complete for all years!")


if __name__ == '__main__':
    main()
