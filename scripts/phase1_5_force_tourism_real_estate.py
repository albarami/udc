#!/usr/bin/env python3
"""
Phase 1.5 Final Fix: Force-categorize Tourism and Real Estate
Strategy: If dataset mentions hotels/tourism/property, it belongs in that category
even if it also mentions "economic" or "indicators"
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import DataSource

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def force_recategorize():
    """
    Force recategorization based on domain-specific keywords.
    Priority: Tourism > Real Estate > Other categories
    """
    
    print("="*80)
    print("FORCE RECATEGORIZATION: Tourism & Real Estate Priority")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    changes = {
        'to_tourism': [],
        'to_real_estate': []
    }
    
    # FORCE TOURISM: Any dataset mentioning hotels/restaurants/tourism
    print("STEP 1: Force Tourism categorization...")
    print("-" * 80)
    
    tourism_assets = db.query(DataSource).filter(
        DataSource.category != 'Tourism & Hospitality',
        DataSource.category != 'Corporate Intelligence',
        DataSource.source_type == 'qatar_open_data'
    ).all()
    
    tourism_keywords = [
        'hotel', 'hotels', 'restaurant', 'restaurants', 'tourism', 'tourist',
        'visitor', 'visitors', 'hospitality', 'accommodation', 'resort',
        'guest', 'guests', 'travel', 'destination', 'attraction'
    ]
    
    for asset in tourism_assets:
        asset_text = f"{asset.source_name} {asset.description or ''}".lower()
        
        if any(keyword in asset_text for keyword in tourism_keywords):
            # Check if it's not a "youth hostel" or "hospital"
            if 'youth' not in asset_text and 'hospital' not in asset_text:
                old_category = asset.category
                asset.category = 'Tourism & Hospitality'
                asset.categorization_confidence = 90  # High confidence for force
                asset.needs_review = False
                changes['to_tourism'].append((asset.source_name, old_category))
    
    db.commit()
    
    print(f"Moved {len(changes['to_tourism'])} datasets to Tourism:\n")
    for name, old_cat in changes['to_tourism'][:10]:
        print(f"  From {old_cat:30} -> {name[:50]}")
    if len(changes['to_tourism']) > 10:
        print(f"  ... and {len(changes['to_tourism']) - 10} more")
    
    # FORCE REAL ESTATE: Property/construction/building/housing datasets
    print("\n\nSTEP 2: Force Real Estate categorization...")
    print("-" * 80)
    
    real_estate_assets = db.query(DataSource).filter(
        DataSource.category != 'Real Estate & Construction',
        DataSource.category != 'Corporate Intelligence',
        DataSource.source_type == 'qatar_open_data'
    ).all()
    
    real_estate_keywords = [
        'property', 'properties', 'real estate', 'building', 'buildings',
        'construction', 'housing', 'residential', 'commercial', 'villa',
        'villas', 'apartment', 'apartments', 'land', 'plot', 'plots',
        'developer', 'contractor', 'permit', 'permits'
    ]
    
    for asset in real_estate_assets:
        asset_text = f"{asset.source_name} {asset.description or ''}".lower()
        
        if any(keyword in asset_text for keyword in real_estate_keywords):
            old_category = asset.category
            asset.category = 'Real Estate & Construction'
            asset.categorization_confidence = 90
            asset.needs_review = False
            changes['to_real_estate'].append((asset.source_name, old_category))
    
    db.commit()
    
    print(f"Moved {len(changes['to_real_estate'])} datasets to Real Estate:\n")
    for name, old_cat in changes['to_real_estate'][:10]:
        print(f"  From {old_cat:30} -> {name[:50]}")
    if len(changes['to_real_estate']) > 10:
        print(f"  ... and {len(changes['to_real_estate']) - 10} more")
    
    # Summary
    print("\n\n" + "="*80)
    print("FINAL DISTRIBUTION")
    print("="*80 + "\n")
    
    results = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM data_sources
        GROUP BY category
        ORDER BY count DESC
    """)).fetchall()
    
    for category, count in results:
        print(f"  {category:40} {count:>4}")
    
    # Focus on critical
    print("\n\nCRITICAL CATEGORIES:")
    print("-" * 80)
    
    for cat in ['Real Estate & Construction', 'Tourism & Hospitality', 'Economic & Financial']:
        count = db.query(DataSource).filter(DataSource.category == cat).count()
        print(f"  {cat:40} {count:>4}")
    
    db.close()
    
    return changes

if __name__ == "__main__":
    force_recategorize()
