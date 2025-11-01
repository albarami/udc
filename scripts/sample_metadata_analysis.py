#!/usr/bin/env python3
"""
Sample and analyze the metadata we have to understand themes and keywords
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
import json

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)

print("="*100)
print("ANALYZING METADATA THEMES AND KEYWORDS")
print("="*100)
print()

with engine.connect() as conn:
    # Get sample of datasets with their metadata
    results = conn.execute(text("""
        SELECT source_name, description, date_range
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        AND date_range IS NOT NULL
        LIMIT 50
    """)).fetchall()
    
    print(f"Analyzing {len(results)} sample datasets...\n")
    
    for i, (name, desc, metadata_json) in enumerate(results, 1):
        try:
            # metadata_json is already a dict from PostgreSQL JSON column
            metadata = metadata_json if metadata_json else {}
            themes = metadata.get('themes', [])
            keywords = metadata.get('keywords', [])
            
            print(f"{i}. {name}")
            if desc:
                print(f"   Description: {desc[:150]}...")
            if themes:
                print(f"   Themes: {themes}")
            if keywords:
                print(f"   Keywords: {keywords}")
            print()
            
        except Exception as e:
            print(f"   Error parsing metadata: {e}")
            print()

engine.dispose()
