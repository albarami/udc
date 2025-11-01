#!/usr/bin/env python3
"""
Phase 1.5: Improved Categorization with Confidence Scoring
Fixes:
- Proper tokenization (no NLTK dependency)
- Guardrails for corporate docs
- Weighted keyword matching
- Confidence scoring
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import DataSource
import re

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def tokenize(text):
    """Simple regex-based tokenization (no NLTK required)"""
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def improved_categorize(source_name, description, source_type):
    """
    Improved categorization with confidence scoring.
    Returns: (category, confidence_score)
    """
    
    # GUARDRAIL 1: Corporate documents always go to Corporate Intelligence
    if source_type in ['corporate_pdf', 'corporate_excel']:
        return 'Corporate Intelligence', 100
    
    # Tokenize title and description
    title_tokens = set(tokenize(source_name))
    desc_tokens = set(tokenize(description)) if description else set()
    all_tokens = title_tokens | desc_tokens
    
    # Category definitions with weighted keywords
    categories = {
        'Real Estate & Construction': {
            'primary': ['property', 'real', 'estate', 'construction', 'building', 'permit', 'land', 'rental'],
            'secondary': ['residential', 'commercial', 'villa', 'apartment', 'ownership'],
            'exclude': []
        },
        'Tourism & Hospitality': {
            'primary': ['tourism', 'hotel', 'visitor', 'hospitality', 'accommodation', 'tourist', 'travel'],
            'secondary': ['guest', 'occupancy', 'booking', 'resort'],
            'exclude': []
        },
        'Infrastructure & Utilities': {
            'primary': ['infrastructure', 'utilities', 'electricity', 'water', 'cooling', 'transport', 'roads'],
            'secondary': ['utility', 'district', 'power', 'sewage', 'waste'],
            'exclude': ['sport', 'airport', 'passport', 'report']  # Exclude false positives
        },
        'Energy & Sustainability': {
            'primary': ['energy', 'sustainability', 'renewable', 'emissions', 'esg', 'environment', 'solar'],
            'secondary': ['climate', 'carbon', 'green', 'ecological'],
            'exclude': []
        },
        'Population & Demographics': {
            'primary': ['population', 'demographic', 'census', 'migration', 'residents', 'household'],
            'secondary': ['births', 'deaths', 'marriages', 'divorces', 'age', 'gender'],
            'exclude': []
        },
        'Employment & Labor': {
            'primary': ['employment', 'labor', 'labour', 'wage', 'salary', 'workforce', 'jobs', 'qatarization'],
            'secondary': ['workers', 'employees', 'compensation', 'occupation'],
            'exclude': []
        },
        'Regional & Global Context': {
            'primary': ['world', 'bank', 'imf', 'united', 'nations', 'gcc', 'regional', 'international'],
            'secondary': ['global', 'benchmark', 'comparative'],
            'exclude': []
        },
        'Economic & Financial': {
            'primary': ['gdp', 'inflation', 'financial', 'economy', 'market', 'revenue', 'profit', 'economic'],
            'secondary': ['fiscal', 'monetary', 'trade', 'investment', 'banking'],
            'exclude': ['quarterly']  # Prevent catching quarterly reports as corporate
        }
    }
    
    # Score each category
    category_scores = {}
    
    for category, keywords in categories.items():
        score = 0
        
        # Check for exclusions first
        if any(excl in all_tokens for excl in keywords['exclude']):
            continue
        
        # Primary keywords (50 points each)
        primary_matches = len([kw for kw in keywords['primary'] if kw in all_tokens])
        score += primary_matches * 50
        
        # Secondary keywords (20 points each)
        secondary_matches = len([kw for kw in keywords['secondary'] if kw in all_tokens])
        score += secondary_matches * 20
        
        # Bonus if keyword in title (30 points)
        if any(kw in title_tokens for kw in keywords['primary']):
            score += 30
        
        category_scores[category] = min(score, 100)  # Cap at 100
    
    # Get best match
    if not category_scores or max(category_scores.values()) == 0:
        # Default to Economic & Financial for Qatar government data
        if source_type == 'qatar_open_data':
            return 'Economic & Financial', 40  # Low confidence default
        return 'Economic & Financial', 30
    
    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    
    return best_category, best_score

def audit_current_state(db):
    """Generate before-state audit"""
    
    print("\n" + "="*80)
    print("PHASE 1.5: CATEGORY AUDIT - BEFORE STATE")
    print("="*80 + "\n")
    
    # Category distribution
    results = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM data_sources
        GROUP BY category
        ORDER BY count DESC
    """)).fetchall()
    
    print("Current Category Distribution:")
    print("-" * 80)
    total = sum(r[1] for r in results)
    
    for category, count in results:
        percentage = (count / total) * 100
        print(f"  {category:40} {count:>4} ({percentage:>5.1f}%)")
    
    print(f"\n  TOTAL: {total:>4}")
    
    # Check for problematic cases
    print("\n\nProblematic Cases:")
    print("-" * 80)
    
    # Case 1: "quarterly" in Corporate Intelligence
    quarterly = db.execute(text("""
        SELECT COUNT(*)
        FROM data_sources
        WHERE category = 'Corporate Intelligence'
        AND source_type = 'qatar_open_data'
        AND (LOWER(source_name) LIKE '%quarterly%' OR LOWER(description) LIKE '%quarterly%')
    """)).scalar()
    
    print(f"  Qatar datasets in Corporate Intelligence: {quarterly}")
    
    # Case 2: "sport" in Infrastructure
    sport = db.execute(text("""
        SELECT COUNT(*)
        FROM data_sources
        WHERE category = 'Infrastructure & Utilities'
        AND (LOWER(source_name) LIKE '%sport%' OR LOWER(description) LIKE '%sport%')
    """)).scalar()
    
    print(f"  Sport datasets in Infrastructure: {sport}")
    
    return {
        'distribution': dict(results),
        'total': total,
        'quarterly_in_corporate': quarterly,
        'sport_in_infrastructure': sport
    }

def recategorize_all_assets(db):
    """Recategorize all 1,180 assets with confidence scores"""
    
    print("\n" + "="*80)
    print("RECATEGORIZING ALL ASSETS")
    print("="*80 + "\n")
    
    assets = db.query(DataSource).all()
    
    changes = {
        'recategorized': 0,
        'unchanged': 0,
        'low_confidence': 0,
        'category_changes': {}
    }
    
    for i, asset in enumerate(assets, 1):
        old_category = asset.category
        
        # Get new category and confidence
        new_category, confidence = improved_categorize(
            asset.source_name,
            asset.description,
            asset.source_type
        )
        
        # Update asset
        asset.category = new_category
        asset.categorization_confidence = confidence
        asset.needs_review = (confidence < 70)
        
        # Track changes
        if old_category != new_category:
            changes['recategorized'] += 1
            key = f"{old_category} -> {new_category}"
            changes['category_changes'][key] = changes['category_changes'].get(key, 0) + 1
        else:
            changes['unchanged'] += 1
        
        if confidence < 70:
            changes['low_confidence'] += 1
        
        # Commit in batches
        if i % 100 == 0:
            db.commit()
            print(f"  Processed {i}/{len(assets)} assets...")
    
    db.commit()
    print(f"\n  COMPLETE: Recategorized all {len(assets)} assets")
    
    return changes

def generate_after_audit(db, before_state, changes):
    """Generate after-state audit and comparison"""
    
    print("\n" + "="*80)
    print("PHASE 1.5: CATEGORY AUDIT - AFTER STATE")
    print("="*80 + "\n")
    
    # New category distribution
    results = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM data_sources
        GROUP BY category
        ORDER BY count DESC
    """)).fetchall()
    
    print("New Category Distribution:")
    print("-" * 80)
    total = sum(r[1] for r in results)
    
    for category, count in results:
        old_count = before_state['distribution'].get(category, 0)
        change = count - old_count
        change_str = f"({change:+d})" if change != 0 else ""
        percentage = (count / total) * 100
        print(f"  {category:40} {count:>4} ({percentage:>5.1f}%) {change_str}")
    
    print(f"\n  TOTAL: {total:>4}")
    
    # Changes summary
    print("\n\nRecategorization Summary:")
    print("-" * 80)
    print(f"  Assets recategorized: {changes['recategorized']}")
    print(f"  Assets unchanged:     {changes['unchanged']}")
    print(f"  Low confidence (<70): {changes['low_confidence']}")
    
    if changes['category_changes']:
        print("\n  Major Category Changes:")
        for change, count in sorted(changes['category_changes'].items(), key=lambda x: -x[1])[:10]:
            print(f"    {change:60} {count:>3}")
    
    # Confidence distribution
    print("\n\nConfidence Distribution:")
    print("-" * 80)
    conf_results = db.execute(text("""
        SELECT 
            CASE 
                WHEN categorization_confidence >= 90 THEN '90-100 (High)'
                WHEN categorization_confidence >= 70 THEN '70-89 (Good)'
                WHEN categorization_confidence >= 50 THEN '50-69 (Fair)'
                ELSE '0-49 (Low)'
            END as conf_range,
            COUNT(*)
        FROM data_sources
        GROUP BY conf_range
        ORDER BY MIN(categorization_confidence) DESC
    """)).fetchall()
    
    for conf_range, count in conf_results:
        percentage = (count / total) * 100
        print(f"  {conf_range:20} {count:>4} ({percentage:>5.1f}%)")
    
    # Assets needing review
    review_count = db.execute(text("""
        SELECT COUNT(*) FROM data_sources WHERE needs_review = TRUE
    """)).scalar()
    
    print(f"\n\n  Assets flagged for manual review: {review_count}")
    
    # Fixed problematic cases
    print("\n\nFixed Problematic Cases:")
    print("-" * 80)
    
    quarterly_now = db.execute(text("""
        SELECT COUNT(*)
        FROM data_sources
        WHERE category = 'Corporate Intelligence'
        AND source_type = 'qatar_open_data'
    """)).scalar()
    
    print(f"  Qatar datasets in Corporate Intelligence:")
    print(f"    Before: {before_state['quarterly_in_corporate']}")
    print(f"    After:  {quarterly_now}")
    print(f"    Fixed:  {before_state['quarterly_in_corporate'] - quarterly_now}")
    
    sport_now = db.execute(text("""
        SELECT COUNT(*)
        FROM data_sources
        WHERE category = 'Infrastructure & Utilities'
        AND (LOWER(source_name) LIKE '%sport%' OR LOWER(description) LIKE '%sport%')
    """)).scalar()
    
    print(f"\n  Sport datasets in Infrastructure:")
    print(f"    Before: {before_state['sport_in_infrastructure']}")
    print(f"    After:  {sport_now}")
    print(f"    Fixed:  {before_state['sport_in_infrastructure'] - sport_now}")

def main():
    """Execute Phase 1.5 recategorization"""
    
    print("="*80)
    print("PHASE 1.5: IMPROVED CATEGORIZATION & CONFIDENCE SCORING")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Step 1: Audit current state
        before_state = audit_current_state(db)
        
        # Step 2: Recategorize all assets
        changes = recategorize_all_assets(db)
        
        # Step 3: Generate after-state audit
        generate_after_audit(db, before_state, changes)
        
        print("\n" + "="*80)
        print("PHASE 1.5 COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("  1. Review assets flagged with needs_review=TRUE")
        print("  2. Manually adjust any remaining edge cases")
        print("  3. Proceed to Phase 2 (ChromaDB embeddings)")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
