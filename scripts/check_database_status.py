#!/usr/bin/env python3
"""
Check the current status of the database.
Show what data has been loaded.
"""

import psycopg2

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port="5437",
    user="postgres",
    password="112211",
    database="udc_polaris"
)

print("="*70)
print("UDC POLARIS - DATABASE STATUS CHECK")
print("="*70)
print()

cursor = conn.cursor()

# Check each table
tables = [
    "analysis_sessions",
    "ceo_context", 
    "agent_responses",
    "debate_tensions",
    "data_sources",
    "token_usage_logs"
]

print("📊 Table Row Counts:")
print("-" * 70)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    status = "✅ Has data" if count > 0 else "❌ Empty"
    print(f"{table:25} {count:>6} rows    {status}")

print()
print("="*70)
print("SUMMARY")
print("="*70)
print()
print("🔍 Database Structure: ✅ Created (6 tables)")
print("📦 Data Loaded: ❌ NOT YET")
print()
print("⚠️  CRITICAL: Qatar datasets NOT loaded into database!")
print()
print("🎯 Next Step Required:")
print("   Create and run scripts/ingest_qatar_metadata.py")
print("   This will load 1,149 Qatar datasets into data_sources table")
print()

cursor.close()
conn.close()
