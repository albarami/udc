#!/usr/bin/env python3
"""
Verify recategorization results and sample specific cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    print("="*80)
    print("RECATEGORIZATION VERIFICATION")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    # Test 1: Verify Corporate Intelligence is clean
    print("TEST 1: Corporate Intelligence (should only be corporate docs)")
    print("-" * 80)
    
    results = db.execute(text("""
        SELECT source_name, source_type, categorization_confidence
        FROM data_sources
        WHERE category = 'Corporate Intelligence'
        LIMIT 10
    """)).fetchall()
    
    for name, stype, conf in results:
        print(f"  {stype:20} (conf:{conf:>3}) {name[:50]}")
    
    # Test 2: Check tourism datasets
    print("\n\nTEST 2: Tourism & Hospitality Datasets")
    print("-" * 80)
    
    results = db.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Tourism & Hospitality'
        LIMIT 10
    """)).fetchall()
    
    for name, conf in results:
        print(f"  (conf:{conf:>3}) {name[:60]}")
    
    # Test 3: Check real estate datasets
    print("\n\nTEST 3: Real Estate & Construction Datasets")
    print("-" * 80)
    
    results = db.execute(text("""
        SELECT source_name, categorization_confidence
        FROM data_sources
        WHERE category = 'Real Estate & Construction'
        LIMIT 10
    """)).fetchall()
    
    for name, conf in results:
        print(f"  (conf:{conf:>3}) {name[:60]}")
    
    # Test 4: Sample of high confidence
    print("\n\nTEST 4: Highest Confidence Assets")
    print("-" * 80)
    
    results = db.execute(text("""
        SELECT category, source_name, categorization_confidence
        FROM data_sources
        ORDER BY categorization_confidence DESC
        LIMIT 10
    """)).fetchall()
    
    for cat, name, conf in results:
        print(f"  {cat:35} (conf:{conf:>3}) {name[:40]}")
    
    # Test 5: Sample of low confidence
    print("\n\nTEST 5: Lowest Confidence Assets (need review)")
    print("-" * 80)
    
    results = db.execute(text("""
        SELECT category, source_name, categorization_confidence
        FROM data_sources
        ORDER BY categorization_confidence ASC
        LIMIT 10
    """)).fetchall()
    
    for cat, name, conf in results:
        print(f"  {cat:35} (conf:{conf:>3}) {name[:40]}")
    
    # Statistics
    print("\n\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    avg_conf = db.execute(text("""
        SELECT AVG(categorization_confidence)::INTEGER
        FROM data_sources
    """)).scalar()
    
    print(f"\nAverage confidence: {avg_conf}")
    
    conf_dist = db.execute(text("""
        SELECT 
            CASE 
                WHEN categorization_confidence = 100 THEN '100 (Perfect)'
                WHEN categorization_confidence >= 90 THEN '90-99 (Excellent)'
                WHEN categorization_confidence >= 70 THEN '70-89 (Good)'
                WHEN categorization_confidence >= 50 THEN '50-69 (Fair)'
                WHEN categorization_confidence >= 30 THEN '30-49 (Low)'
                ELSE '0-29 (Very Low)'
            END as range,
            COUNT(*)
        FROM data_sources
        GROUP BY range
        ORDER BY MIN(categorization_confidence) DESC
    """)).fetchall()
    
    print("\nConfidence Distribution:")
    for range_name, count in conf_dist:
        print(f"  {range_name:20} {count:>4}")
    
    db.close()

if __name__ == "__main__":
    main()
