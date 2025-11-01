#!/usr/bin/env python3
"""
Phase 1.5 Step 1: Add confidence scoring columns
"""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)

print("Adding confidence scoring columns...")

with engine.connect() as conn:
    # Add confidence score column
    conn.execute(text("""
        ALTER TABLE data_sources 
        ADD COLUMN IF NOT EXISTS categorization_confidence INTEGER DEFAULT 0
    """))
    
    # Add review flag column
    conn.execute(text("""
        ALTER TABLE data_sources 
        ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE
    """))
    
    conn.commit()
    
    print("SUCCESS - Columns added:")
    print("  - categorization_confidence (INTEGER)")
    print("  - needs_review (BOOLEAN)")

engine.dispose()
