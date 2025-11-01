#!/usr/bin/env python3
"""
Export ALL datasets to a readable file for manual review
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
import json

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)

output = []

with engine.connect() as conn:
    results = conn.execute(text("""
        SELECT 
            category,
            source_name,
            description,
            categorization_confidence,
            source_type
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        ORDER BY category, categorization_confidence DESC, source_name
    """)).fetchall()
    
    current_category = None
    
    for category, name, desc, conf, source_type in results:
        if category != current_category:
            output.append(f"\n\n{'='*100}")
            output.append(f"CATEGORY: {category}")
            output.append(f"{'='*100}\n")
            current_category = category
        
        output.append(f"[Confidence: {conf:>3}] {name}")
        if desc:
            # Clean and format description
            desc_clean = desc.replace('\n', ' ').strip()
            if len(desc_clean) > 200:
                desc_clean = desc_clean[:200] + "..."
            output.append(f"    Description: {desc_clean}")
        output.append("")

# Save to file
output_path = Path("d:/udc/data/DATASET_REVIEW_ALL_1149.txt")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Exported all 1,149 datasets to: {output_path}")
print(f"Total lines: {len(output)}")
print()
print("Now you can read this file and understand what data we actually have.")
print("Look for:")
print("  - Datasets in wrong categories")
print("  - UDC-specific real estate data")
print("  - Tourism/hospitality patterns")
print("  - Economic indicators that should be elsewhere")

engine.dispose()
