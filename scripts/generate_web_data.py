#!/usr/bin/env -S uvx --with duckdb python3
"""
Generate JSON data files for the web interface from Parquet files.
"""

import json
import duckdb
import os


def generate_top_taxpayers_across_years(conn, years):
    """Generate top 1000 taxpayers across all years."""

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
        LIMIT 1000
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
        LIMIT 1000
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
        LIMIT 1000
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

    # Look up 2013 NTN for individuals with unique names
    unique_2013_names = conn.execute("""
        SELECT name, ntn_8, tax_paid
        FROM 'docs/data/2013/individuals.parquet'
        WHERE name IN (
            SELECT name FROM 'docs/data/2013/individuals.parquet'
            GROUP BY name HAVING COUNT(*) = 1
        )
    """).fetchall()

    # Create lookup dict: name -> (ntn_8, tax_paid)
    name_to_2013 = {row[0]: (row[1], row[2]) for row in unique_2013_names}

    # Enrich individuals_data with 2013 info
    for person in individuals_data:
        if person['name'] in name_to_2013:
            ntn, tax = name_to_2013[person['name']]
            person['ntn_2013'] = ntn
            # Only add tax if it wasn't already there (it shouldn't be for CNIC-based records)
            if person['years']['2013'] == 0:
                person['years']['2013'] = tax
                person['total'] += tax

    # Re-sort by total after adding 2013 data
    individuals_data.sort(key=lambda x: x['total'], reverse=True)

    return {
        'companies': companies_data,
        'aop': aop_data,
        'individuals': individuals_data
    }


def main():
    os.makedirs('docs/data/web', exist_ok=True)
    conn = duckdb.connect()

    years = [2013, 2014, 2015, 2016, 2017, 2018]

    print("\nGenerating across-years top 1000...")
    across_years = generate_top_taxpayers_across_years(conn, years)
    with open('docs/data/web/top_taxpayers_across_years.json', 'w') as f:
        json.dump(across_years, f, indent=2)
    print("  Written: docs/data/web/top_taxpayers_across_years.json")

    conn.close()
    print("\nWeb data generation complete!")


if __name__ == '__main__':
    main()
