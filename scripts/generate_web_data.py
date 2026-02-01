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

    companies = conn.execute("""
        WITH yearly_aggregated AS (
            SELECT
                ntn_7,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(id ORDER BY year DESC) as ntn
            FROM 'docs/data/all.parquet'
            WHERE category = 'company' AND tax_paid > 0
            GROUP BY ntn_7, year
        ),
        aggregated AS (
            SELECT
                ntn_7,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn,
                SUM(year_tax) as total_tax,
                MAP_FROM_ENTRIES(LIST(ROW(year, year_tax) ORDER BY year)) as year_breakdown
            FROM yearly_aggregated
            GROUP BY ntn_7
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

    aop = conn.execute("""
        WITH yearly_aggregated AS (
            SELECT
                ntn_7,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(id ORDER BY year DESC) as ntn
            FROM 'docs/data/all.parquet'
            WHERE category = 'aop' AND tax_paid > 0
            GROUP BY ntn_7, year
        ),
        aggregated AS (
            SELECT
                ntn_7,
                FIRST(name ORDER BY year DESC) as name,
                FIRST(ntn ORDER BY year DESC) as ntn,
                SUM(year_tax) as total_tax,
                MAP_FROM_ENTRIES(LIST(ROW(year, year_tax) ORDER BY year)) as year_breakdown
            FROM yearly_aggregated
            GROUP BY ntn_7
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

    individuals = conn.execute("""
        WITH yearly_aggregated AS (
            SELECT
                id,
                year,
                SUM(tax_paid) as year_tax,
                FIRST(name ORDER BY year DESC) as name
            FROM 'docs/data/all.parquet'
            WHERE category = 'individual' AND tax_paid > 0
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
        SELECT name, id as ntn_8, tax_paid
        FROM 'docs/data/all.parquet'
        WHERE category = 'individual' AND year = 2013
        AND name IN (
            SELECT name
            FROM 'docs/data/all.parquet'
            WHERE category = 'individual' AND year = 2013
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


def generate_tax_trends_by_year_and_category(conn, years):
    """Generate tax collected per year, broken down by category."""

    print("\nGenerating tax trends by year and category...")

    result = conn.execute("""
        SELECT
            year,
            category,
            SUM(tax_paid) as total_tax,
            COUNT(*) as entity_count
        FROM 'docs/data/all.parquet'
        WHERE tax_paid > 0
        GROUP BY year, category
        ORDER BY year, category
    """).fetchall()

    trends = {}
    for row in result:
        year = str(row[0])
        category = row[1]
        if year not in trends:
            trends[year] = {}
        trends[year][category] = {
            'tax': row[2],
            'entities': row[3]
        }

    return trends


def generate_category_summary(conn):
    """Generate summary stats for each category."""

    print("\nGenerating category summary...")

    result = conn.execute("""
        SELECT
            category,
            SUM(tax_paid) as total_tax,
            COUNT(*) as entity_count,
            AVG(tax_paid) as avg_tax,
            MAX(tax_paid) as max_tax
        FROM 'docs/data/all.parquet'
        WHERE tax_paid > 0
        GROUP BY category
    """).fetchall()

    categories = {}
    for row in result:
        categories[row[0]] = {
            'total_tax': row[1],
            'entity_count': row[2],
            'avg_tax': row[3],
            'max_tax': row[4]
        }

    return categories


def generate_tax_distribution_histogram(conn):
    """Generate histogram of tax paid amounts in brackets."""

    print("\nGenerating tax distribution histogram...")

    # Define tax brackets
    brackets = [
        (0, 100000, '0-100k'),
        (100000, 500000, '100k-500k'),
        (500000, 1000000, '500k-1M'),
        (1000000, 5000000, '1M-5M'),
        (5000000, 10000000, '5M-10M'),
        (10000000, float('inf'), '10M+')
    ]

    histogram = {}
    for min_val, max_val, label in brackets:
        if max_val == float('inf'):
            count = conn.execute(f"""
                SELECT COUNT(*) FROM 'docs/data/all.parquet'
                WHERE tax_paid >= {min_val}
            """).fetchone()[0]
        else:
            count = conn.execute(f"""
                SELECT COUNT(*) FROM 'docs/data/all.parquet'
                WHERE tax_paid >= {min_val} AND tax_paid < {max_val}
            """).fetchone()[0]
        histogram[label] = count

    return histogram


def generate_entity_growth_over_time(conn, years):
    """Generate count of distinct entities per year."""

    print("\nGenerating entity growth over time...")

    growth = {}
    for year in years:
        count = conn.execute(f"""
            SELECT COUNT(DISTINCT CASE
                WHEN category = 'individual' THEN id
                ELSE ntn_7
            END) FROM 'docs/data/all.parquet'
            WHERE year = {year}
        """).fetchone()[0]
        growth[str(year)] = count

    return growth


def main():
    os.makedirs('docs/data/web', exist_ok=True)
    conn = duckdb.connect()

    years = [2013, 2014, 2015, 2016, 2017, 2018]

    print("\nGenerating across-years top 1000...")
    across_years = generate_top_taxpayers_across_years(conn, years)
    with open('docs/data/web/top_taxpayers_across_years.json', 'w') as f:
        json.dump(across_years, f, indent=2)
    print("  Written: docs/data/web/top_taxpayers_across_years.json")

    print("\nGenerating visualization data...")

    tax_trends = generate_tax_trends_by_year_and_category(conn, years)
    with open('docs/data/web/tax_trends.json', 'w') as f:
        json.dump(tax_trends, f, indent=2)
    print("  Written: docs/data/web/tax_trends.json")

    category_summary = generate_category_summary(conn)
    with open('docs/data/web/category_summary.json', 'w') as f:
        json.dump(category_summary, f, indent=2)
    print("  Written: docs/data/web/category_summary.json")

    tax_distribution = generate_tax_distribution_histogram(conn)
    with open('docs/data/web/tax_distribution.json', 'w') as f:
        json.dump(tax_distribution, f, indent=2)
    print("  Written: docs/data/web/tax_distribution.json")

    entity_growth = generate_entity_growth_over_time(conn, years)
    with open('docs/data/web/entity_growth.json', 'w') as f:
        json.dump(entity_growth, f, indent=2)
    print("  Written: docs/data/web/entity_growth.json")

    conn.close()
    print("\nWeb data generation complete!")


if __name__ == '__main__':
    main()
