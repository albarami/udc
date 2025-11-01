#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect("host=localhost port=5437 user=postgres password=112211 dbname=udc_polaris")
cur = conn.cursor()

# Check column exists
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='data_sources' 
    AND column_name LIKE '%conf%'
""")

print("Columns with 'conf' in name:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check sample values
cur.execute("""
    SELECT id, source_name, categorization_confidence
    FROM data_sources
    LIMIT 5
""")

print("\nSample rows:")
for row in cur.fetchall():
    print(f"  ID: {row[0][:20]}... | Name: {row[1][:30]}... | Conf: {row[2]}")

conn.close()
