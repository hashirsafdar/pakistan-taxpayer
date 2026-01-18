#!/usr/bin/env python3
"""
Create consolidated Parquet file from all year/category files.

Combines 18 files (2013-2018, 3 categories each) into docs/data/all.parquet
with unified schema and optimized sort order for HTTP range request pruning.
"""

import duckdb

# Years and categories to consolidate
YEARS = [2013, 2014, 2015, 2016, 2017, 2018]
CATEGORIES = {
    'companies': 'company',
    'aop': 'aop',
    'individuals': 'individual'
}

def main():
    con = duckdb.connect()

    # Build UNION ALL query for all year/category combinations
    union_queries = []

    for year in YEARS:
        for file_category, category_name in CATEGORIES.items():
            file_path = f"docs/data/{year}/{file_category}.parquet"

            # Normalize column names based on year
            if year in [2017, 2018]:
                # These have 'sr' column which we drop
                # Schema: sr, name, ntn_7/cnic, tax_paid
                id_col = 'ntn_7' if file_category in ['companies', 'aop'] else 'cnic'
                query = f"""
                    SELECT
                        {year} AS year,
                        '{category_name}' AS category,
                        name,
                        "{id_col}" AS id,
                        tax_paid
                    FROM '{file_path}'
                """
            else:
                # 2013-2016: name, ntn_8/cnic, tax_paid
                id_col = 'ntn_8' if file_category in ['companies', 'aop'] else 'cnic'
                # Special case: 2013 individuals also use ntn_8
                if year == 2013 and file_category == 'individuals':
                    id_col = 'ntn_8'

                query = f"""
                    SELECT
                        {year} AS year,
                        '{category_name}' AS category,
                        name,
                        "{id_col}" AS id,
                        tax_paid
                    FROM '{file_path}'
                """

            union_queries.append(query)

    # Combine all queries with UNION ALL
    combined_query = " UNION ALL ".join(union_queries)

    # Create final query with computed columns and sort order
    final_query = f"""
        COPY (
            SELECT
                year,
                category,
                name,
                id,
                CASE
                    WHEN category IN ('company', 'aop') THEN 'ntn'
                    WHEN year = 2013 AND category = 'individual' THEN 'ntn'
                    WHEN LENGTH(id) <= 8 THEN 'ntn'
                    ELSE 'cnic'
                END AS id_type,
                CASE
                    WHEN category IN ('company', 'aop') THEN LEFT(id, 7)
                    WHEN year = 2013 AND category = 'individual' THEN LEFT(id, 7)
                    WHEN LENGTH(id) <= 8 THEN LEFT(id, 7)
                    ELSE NULL
                END AS ntn_7,
                tax_paid
            FROM ({combined_query})
            ORDER BY id_type, ntn_7 NULLS LAST, id, year, category
        ) TO 'docs/data/all.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """

    print("Creating consolidated Parquet file...")
    print(f"Reading {len(YEARS)} years × {len(CATEGORIES)} categories = {len(union_queries)} files")

    con.execute(final_query)

    # Verify results
    result = con.execute("SELECT COUNT(*) FROM 'docs/data/all.parquet'").fetchone()
    print(f"✓ Created docs/data/all.parquet with {result[0]:,} records")

    # Show schema
    print("\nSchema:")
    schema = con.execute("DESCRIBE SELECT * FROM 'docs/data/all.parquet'").fetchall()
    for row in schema:
        print(f"  {row[0]:<12} {row[1]}")

    # Show sample distribution
    print("\nRecord distribution:")
    dist = con.execute("""
        SELECT year, category, COUNT(*) as count
        FROM 'docs/data/all.parquet'
        GROUP BY year, category
        ORDER BY year, category
    """).fetchall()
    for row in dist:
        print(f"  {row[0]} {row[1]:<10} {row[2]:>8,}")

    con.close()

if __name__ == "__main__":
    main()
