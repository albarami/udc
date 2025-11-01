#!/usr/bin/env python3
"""
Deep Analysis: Actually understand what data we have
Read every dataset title, understand the content, make informed decisions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
import json

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)

print("="*80)
print("DEEP DATA ANALYSIS - UNDERSTANDING WHAT WE ACTUALLY HAVE")
print("="*80)
print()

with engine.connect() as conn:
    # Let's look at EVERY dataset currently in each category
    # and understand if it truly belongs there
    
    categories = [
        'Real Estate & Construction',
        'Tourism & Hospitality',
        'Economic & Financial',
        'Infrastructure & Utilities',
        'Population & Demographics',
        'Employment & Labor',
        'Energy & Sustainability',
        'Regional & Global Context',
        'Corporate Intelligence'
    ]
    
    for category in categories:
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category}")
        print(f"{'='*80}\n")
        
        results = conn.execute(text("""
            SELECT source_name, description, categorization_confidence
            FROM data_sources
            WHERE category = :cat
            AND source_type = 'qatar_open_data'
            ORDER BY categorization_confidence DESC, source_name
        """), {'cat': category}).fetchall()
        
        print(f"Total: {len(results)} datasets\n")
        
        # Show ALL datasets in this category
        for i, (name, desc, conf) in enumerate(results, 1):
            desc_short = (desc[:100] + '...') if desc and len(desc) > 100 else (desc or 'No description')
            print(f"{i:3}. [{conf:>3}] {name}")
            if desc:
                print(f"     Description: {desc_short}")
            print()
        
        # Pause between categories for readability
        print("\n" + "-"*80)
        input("Press Enter to see next category...")

engine.dispose()
