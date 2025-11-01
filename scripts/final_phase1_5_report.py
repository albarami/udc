#!/usr/bin/env python3
"""
Final Phase 1.5 Report - Fresh database query
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"

conn = psycopg2.connect("host=localhost port=5437 user=postgres password=112211 dbname=udc_polaris")
cursor = conn.cursor()

print("="*80)
print("PHASE 1.5 FINAL REPORT")
print("="*80 + "\n")

# Category distribution
print("Category Distribution:")
print("-" * 80)
cursor.execute("""
    SELECT category, COUNT(*) as count
    FROM data_sources
    GROUP BY category
    ORDER BY count DESC
""")

for category, count in cursor.fetchall():
    print(f"  {category:40} {count:>4}")

# Confidence distribution
print("\n\nConfidence Distribution:")
print("-" * 80)
cursor.execute("""
    SELECT 
        CASE 
            WHEN categorization_confidence >= 90 THEN '90-100 (Excellent)'
            WHEN categorization_confidence >= 70 THEN '70-89 (Good)'
            WHEN categorization_confidence >= 50 THEN '50-69 (Fair)'
            WHEN categorization_confidence >= 30 THEN '30-49 (Low)'
            ELSE '0-29 (Very Low)'
        END as range,
        COUNT(*)
    FROM data_sources
    GROUP BY range
    ORDER BY MIN(categorization_confidence) DESC
""")

for range_name, count in cursor.fetchall():
    print(f"  {range_name:25} {count:>4}")

# Average confidence
cursor.execute("""
    SELECT AVG(categorization_confidence)::INTEGER
    FROM data_sources
""")
avg_conf = cursor.fetchone()[0]
print(f"\n  Average confidence: {avg_conf}")

# Corporate Intelligence check
print("\n\nCorporate Intelligence Verification:")
print("-" * 80)
cursor.execute("""
    SELECT COUNT(*), source_type
    FROM data_sources
    WHERE category = 'Corporate Intelligence'
    GROUP BY source_type
""")

for count, stype in cursor.fetchall():
    print(f"  {stype:25} {count:>4}")

# High confidence samples
print("\n\nHigh Confidence Samples (>=80):")
print("-" * 80)
cursor.execute("""
    SELECT category, source_name, categorization_confidence
    FROM data_sources
    WHERE categorization_confidence >= 80
    ORDER BY categorization_confidence DESC
    LIMIT 10
""")

for category, name, conf in cursor.fetchall():
    print(f"  [{conf:>3}] {category:30} {name[:40]}")

# Assets needing review
cursor.execute("""
    SELECT COUNT(*) FROM data_sources WHERE needs_review = TRUE
""")
review_count = cursor.fetchone()[0]

print(f"\n\n  Assets flagged for review: {review_count}")

print("\n" + "="*80)
print("PHASE 1.5 COMPLETE")
print("="*80)

cursor.close()
conn.close()
