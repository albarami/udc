#!/usr/bin/env python3
"""
Fix confidence scores - recalculate and update properly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import DataSource
import re

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def tokenize(text):
    """Simple regex tokenization"""
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def calculate_confidence(source_name, description, source_type, category):
    """Calculate confidence score for the assigned category"""
    
    # Corporate docs always 100%
    if source_type in ['corporate_pdf', 'corporate_excel']:
        return 100
    
    # Tokenize
    title_tokens = set(tokenize(source_name))
    desc_tokens = set(tokenize(description)) if description else set()
    all_tokens = title_tokens | desc_tokens
    
    # Category keywords
    category_keywords = {
        'Real Estate & Construction': {
            'primary': ['property', 'real', 'estate', 'construction', 'building', 'permit', 'land'],
            'secondary': ['residential', 'commercial', 'villa', 'apartment']
        },
        'Tourism & Hospitality': {
            'primary': ['tourism', 'hotel', 'visitor', 'hospitality', 'accommodation', 'tourist'],
            'secondary': ['guest', 'occupancy', 'booking', 'resort']
        },
        'Infrastructure & Utilities': {
            'primary': ['infrastructure', 'utilities', 'electricity', 'water', 'cooling', 'transport'],
            'secondary': ['utility', 'district', 'power', 'sewage']
        },
        'Energy & Sustainability': {
            'primary': ['energy', 'sustainability', 'renewable', 'emissions', 'esg'],
            'secondary': ['climate', 'carbon', 'green']
        },
        'Population & Demographics': {
            'primary': ['population', 'demographic', 'census', 'migration', 'residents'],
            'secondary': ['births', 'deaths', 'marriages', 'age', 'gender']
        },
        'Employment & Labor': {
            'primary': ['employment', 'labor', 'labour', 'wage', 'salary', 'workforce'],
            'secondary': ['workers', 'employees', 'compensation']
        },
        'Regional & Global Context': {
            'primary': ['world', 'bank', 'imf', 'nations', 'gcc', 'regional'],
            'secondary': ['global', 'benchmark', 'comparative']
        },
        'Economic & Financial': {
            'primary': ['gdp', 'inflation', 'financial', 'economy', 'market'],
            'secondary': ['fiscal', 'monetary', 'trade', 'investment']
        },
        'Corporate Intelligence': {
            'primary': ['annual', 'report', 'quarterly', 'investor'],
            'secondary': ['corporate', 'company', 'financial', 'statement']
        }
    }
    
    keywords = category_keywords.get(category, {'primary': [], 'secondary': []})
    
    score = 0
    
    # Primary keywords (50 points each)
    primary_matches = len([kw for kw in keywords['primary'] if kw in all_tokens])
    score += primary_matches * 50
    
    # Secondary keywords (20 points each)
    secondary_matches = len([kw for kw in keywords['secondary'] if kw in all_tokens])
    score += secondary_matches * 20
    
    # Bonus if in title
    if any(kw in title_tokens for kw in keywords['primary']):
        score += 30
    
    return min(score, 100)

def main():
    print("="*80)
    print("FIXING CONFIDENCE SCORES")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    assets = db.query(DataSource).all()
    
    high_conf = 0
    medium_conf = 0
    low_conf = 0
    
    for i, asset in enumerate(assets, 1):
        # Calculate confidence
        conf = calculate_confidence(
            asset.source_name,
            asset.description,
            asset.source_type,
            asset.category
        )
        
        # Update
        asset.categorization_confidence = conf
        asset.needs_review = (conf < 70)
        
        # Count
        if conf >= 70:
            high_conf += 1
        elif conf >= 50:
            medium_conf += 1
        else:
            low_conf += 1
        
        if i % 100 == 0:
            db.commit()
            print(f"  Processed {i}/{len(assets)}...")
    
    db.commit()
    
    print(f"\n  COMPLETE: Updated confidence scores for all {len(assets)} assets")
    print(f"\n  High confidence (>=70): {high_conf}")
    print(f"  Medium confidence (50-69): {medium_conf}")
    print(f"  Low confidence (<50): {low_conf}")
    
    db.close()

if __name__ == "__main__":
    main()
