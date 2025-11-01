#!/usr/bin/env python3
"""
Analyze what's actually in Economic & Financial to understand why
Real Estate and Tourism are under-represented.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)

print("="*80)
print("ANALYZING ECONOMIC & FINANCIAL CATEGORY")
print("="*80 + "\n")

with engine.connect() as conn:
    # Sample datasets that might be Real Estate
    print("POTENTIAL REAL ESTATE DATASETS (in Economic):")
    print("-" * 80)
    
    results = conn.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Economic & Financial'
        AND (
            LOWER(source_name) LIKE '%property%'
            OR LOWER(source_name) LIKE '%building%'
            OR LOWER(source_name) LIKE '%construction%'
            OR LOWER(source_name) LIKE '%housing%'
            OR LOWER(source_name) LIKE '%residential%'
            OR LOWER(source_name) LIKE '%land%'
        )
        LIMIT 20
    """)).fetchall()
    
    print(f"Found {len(results)} potential Real Estate datasets:\n")
    for name, conf in results:
        print(f"  [{conf:>3}] {name[:70]}")
    
    # Sample datasets that might be Tourism
    print("\n\nPOTENTIAL TOURISM DATASETS (in Economic):")
    print("-" * 80)
    
    results = conn.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Economic & Financial'
        AND (
            LOWER(source_name) LIKE '%hotel%'
            OR LOWER(source_name) LIKE '%tourism%'
            OR LOWER(source_name) LIKE '%visitor%'
            OR LOWER(source_name) LIKE '%hospitality%'
            OR LOWER(source_name) LIKE '%accommodation%'
            OR LOWER(source_name) LIKE '%travel%'
        )
        LIMIT 20
    """)).fetchall()
    
    print(f"Found {len(results)} potential Tourism datasets:\n")
    for name, conf in results:
        print(f"  [{conf:>3}] {name[:70]}")
    
    # What's actually IN Real Estate category?
    print("\n\nCURRENT REAL ESTATE CATEGORY (All 20 datasets):")
    print("-" * 80)
    
    results = conn.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Real Estate & Construction'
        ORDER BY categorization_confidence DESC
    """)).fetchall()
    
    for name, conf in results:
        print(f"  [{conf:>3}] {name[:70]}")
    
    # What's actually IN Tourism category?
    print("\n\nCURRENT TOURISM CATEGORY (All 15 datasets):")
    print("-" * 80)
    
    results = conn.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Tourism & Hospitality'
        ORDER BY categorization_confidence DESC
    """)).fetchall()
    
    for name, conf in results:
        print(f"  [{conf:>3}] {name[:70]}")

engine.dispose()
