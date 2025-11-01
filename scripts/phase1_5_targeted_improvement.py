#!/usr/bin/env python3
"""
Phase 1.5 Targeted Improvement: Fix Real Estate & Tourism under-representation
Focus: Move miscategorized datasets from Economic & Financial to proper categories
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
    """Regex tokenization"""
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def enhanced_categorize(source_name, description, source_type):
    """
    Enhanced categorization with stronger Real Estate & Tourism focus.
    Priority order matters - check most specific categories first.
    """
    
    # GUARDRAIL: Corporate documents
    if source_type in ['corporate_pdf', 'corporate_excel']:
        return 'Corporate Intelligence', 100
    
    # Tokenize
    title_tokens = set(tokenize(source_name))
    desc_tokens = set(tokenize(description)) if description else set()
    all_tokens = title_tokens | desc_tokens
    text = f"{source_name} {description}".lower()
    
    # ENHANCED CATEGORIES - Priority order
    
    # 1. REAL ESTATE & CONSTRUCTION (Most specific - check first)
    real_estate_primary = [
        'property', 'real', 'estate', 'land', 'plot', 
        'residential', 'commercial', 'villa', 'apartment',
        'housing', 'development', 'developer', 'contractor',
        'building', 'construction', 'permit'
    ]
    real_estate_secondary = [
        'ownership', 'occupancy', 'rental', 'lease', 'mortgage',
        'zoning', 'planning', 'urban'
    ]
    
    re_score = 0
    re_primary_matches = len([kw for kw in real_estate_primary if kw in all_tokens])
    re_secondary_matches = len([kw for kw in real_estate_secondary if kw in all_tokens])
    
    if re_primary_matches > 0:
        re_score = re_primary_matches * 50 + re_secondary_matches * 20
        if any(kw in title_tokens for kw in real_estate_primary):
            re_score += 30
        if re_score >= 70:
            return 'Real Estate & Construction', min(re_score, 100)
    
    # 2. TOURISM & HOSPITALITY (High priority - check second)
    tourism_primary = [
        'tourism', 'hotel', 'hospitality', 'visitor', 'tourist',
        'resort', 'accommodation', 'guest', 'attraction', 'leisure',
        'travel', 'destination'
    ]
    tourism_secondary = [
        'occupancy', 'booking', 'entertainment', 'cultural',
        'museum', 'heritage', 'recreation'
    ]
    
    # Exclusion: Don't catch "youth hostel" or "hospital"
    if 'youth' in all_tokens or 'hospital' in all_tokens:
        tourism_exclude = True
    else:
        tourism_exclude = False
    
    if not tourism_exclude:
        tour_score = 0
        tour_primary_matches = len([kw for kw in tourism_primary if kw in all_tokens])
        tour_secondary_matches = len([kw for kw in tourism_secondary if kw in all_tokens])
        
        if tour_primary_matches > 0:
            tour_score = tour_primary_matches * 50 + tour_secondary_matches * 20
            if any(kw in title_tokens for kw in tourism_primary):
                tour_score += 30
            if tour_score >= 70:
                return 'Tourism & Hospitality', min(tour_score, 100)
    
    # 3. POPULATION & DEMOGRAPHICS
    population_primary = [
        'population', 'demographic', 'census', 'birth', 'death',
        'marriage', 'divorce', 'migration', 'residents', 'household',
        'age', 'gender', 'nationality'
    ]
    
    pop_score = 0
    pop_matches = len([kw for kw in population_primary if kw in all_tokens])
    if pop_matches >= 2:  # Need at least 2 keywords
        pop_score = pop_matches * 50
        if any(kw in title_tokens for kw in population_primary):
            pop_score += 30
        if pop_score >= 70:
            return 'Population & Demographics', min(pop_score, 100)
    
    # 4. EMPLOYMENT & LABOR
    employment_primary = [
        'employment', 'labor', 'labour', 'wage', 'salary', 'workforce',
        'jobs', 'workers', 'employees', 'qatarization', 'occupation',
        'compensation'
    ]
    
    emp_score = 0
    emp_matches = len([kw for kw in employment_primary if kw in all_tokens])
    if emp_matches >= 2:
        emp_score = emp_matches * 50
        if any(kw in title_tokens for kw in employment_primary):
            emp_score += 30
        if emp_score >= 70:
            return 'Employment & Labor', min(emp_score, 100)
    
    # 5. INFRASTRUCTURE & UTILITIES
    infrastructure_primary = [
        'infrastructure', 'utilities', 'electricity', 'water', 'cooling',
        'transport', 'roads', 'utility', 'district', 'power', 'sewage',
        'waste', 'network'
    ]
    
    # EXCLUSION: sport, airport, passport, report
    infra_exclude = any(word in all_tokens for word in ['sport', 'airport', 'passport'])
    
    if not infra_exclude:
        infra_score = 0
        infra_matches = len([kw for kw in infrastructure_primary if kw in all_tokens])
        if infra_matches >= 2:
            infra_score = infra_matches * 50
            if any(kw in title_tokens for kw in infrastructure_primary):
                infra_score += 30
            if infra_score >= 70:
                return 'Infrastructure & Utilities', min(infra_score, 100)
    
    # 6. ENERGY & SUSTAINABILITY
    energy_primary = [
        'energy', 'sustainability', 'renewable', 'emissions', 'esg',
        'environment', 'solar', 'climate', 'carbon', 'green', 'ecological'
    ]
    
    energy_score = 0
    energy_matches = len([kw for kw in energy_primary if kw in all_tokens])
    if energy_matches >= 2:
        energy_score = energy_matches * 50
        if any(kw in title_tokens for kw in energy_primary):
            energy_score += 30
        if energy_score >= 70:
            return 'Energy & Sustainability', min(energy_score, 100)
    
    # 7. REGIONAL & GLOBAL CONTEXT
    regional_primary = [
        'world', 'bank', 'imf', 'united', 'nations', 'gcc',
        'regional', 'international', 'global', 'benchmark', 'comparative'
    ]
    
    regional_score = 0
    regional_matches = len([kw for kw in regional_primary if kw in all_tokens])
    if regional_matches >= 2:
        regional_score = regional_matches * 50
        if any(kw in title_tokens for kw in regional_primary):
            regional_score += 30
        if regional_score >= 70:
            return 'Regional & Global Context', min(regional_score, 100)
    
    # 8. ECONOMIC & FINANCIAL (Default catch-all)
    economic_primary = [
        'gdp', 'inflation', 'financial', 'economy', 'market', 'revenue',
        'profit', 'fiscal', 'monetary', 'trade', 'investment', 'banking',
        'economic', 'indicator'
    ]
    
    eco_score = 0
    eco_matches = len([kw for kw in economic_primary if kw in all_tokens])
    if eco_matches > 0:
        eco_score = eco_matches * 40  # Lower weight for catch-all
        if any(kw in title_tokens for kw in economic_primary):
            eco_score += 20
        return 'Economic & Financial', min(eco_score, 100)
    
    # Fallback
    return 'Economic & Financial', 30

def audit_before_state(db):
    """Audit current state"""
    
    print("\n" + "="*80)
    print("BEFORE STATE: Current Distribution")
    print("="*80 + "\n")
    
    results = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM data_sources
        GROUP BY category
        ORDER BY count DESC
    """)).fetchall()
    
    before = {}
    for category, count in results:
        before[category] = count
        print(f"  {category:40} {count:>4}")
    
    print(f"\n  TOTAL: {sum(before.values())}")
    
    return before

def recategorize_low_confidence(db):
    """Focus on recategorizing low-confidence assets"""
    
    print("\n" + "="*80)
    print("RECATEGORIZING LOW-CONFIDENCE ASSETS")
    print("="*80 + "\n")
    
    # Focus on Economic & Financial with low confidence
    assets = db.query(DataSource).filter(
        DataSource.category == 'Economic & Financial',
        DataSource.categorization_confidence < 70
    ).all()
    
    print(f"Processing {len(assets)} low-confidence Economic & Financial assets...\n")
    
    changes = {
        'to_real_estate': 0,
        'to_tourism': 0,
        'to_population': 0,
        'to_employment': 0,
        'to_infrastructure': 0,
        'unchanged': 0
    }
    
    for i, asset in enumerate(assets, 1):
        old_category = asset.category
        
        new_category, confidence = enhanced_categorize(
            asset.source_name,
            asset.description,
            asset.source_type
        )
        
        asset.category = new_category
        asset.categorization_confidence = confidence
        asset.needs_review = (confidence < 70)
        
        if old_category != new_category:
            if new_category == 'Real Estate & Construction':
                changes['to_real_estate'] += 1
            elif new_category == 'Tourism & Hospitality':
                changes['to_tourism'] += 1
            elif new_category == 'Population & Demographics':
                changes['to_population'] += 1
            elif new_category == 'Employment & Labor':
                changes['to_employment'] += 1
            elif new_category == 'Infrastructure & Utilities':
                changes['to_infrastructure'] += 1
        else:
            changes['unchanged'] += 1
        
        if i % 100 == 0:
            db.commit()
            print(f"  Processed {i}/{len(assets)}...")
    
    db.commit()
    
    print(f"\n  COMPLETE: Processed {len(assets)} assets\n")
    print("Changes:")
    print(f"  Moved to Real Estate: {changes['to_real_estate']}")
    print(f"  Moved to Tourism: {changes['to_tourism']}")
    print(f"  Moved to Population: {changes['to_population']}")
    print(f"  Moved to Employment: {changes['to_employment']}")
    print(f"  Moved to Infrastructure: {changes['to_infrastructure']}")
    print(f"  Remained in Economic: {changes['unchanged']}")
    
    return changes

def audit_after_state(db, before):
    """Audit after state and compare"""
    
    print("\n" + "="*80)
    print("AFTER STATE: New Distribution")
    print("="*80 + "\n")
    
    results = db.execute(text("""
        SELECT category, COUNT(*) as count
        FROM data_sources
        GROUP BY category
        ORDER BY count DESC
    """)).fetchall()
    
    print(f"  {'Category':<40} {'Count':>6} {'Change':>8}")
    print("  " + "-"*76)
    
    for category, count in results:
        old_count = before.get(category, 0)
        change = count - old_count
        change_str = f"({change:+d})" if change != 0 else ""
        print(f"  {category:<40} {count:>6} {change_str:>8}")
    
    # Focus on critical categories
    print("\n\nCRITICAL CATEGORIES:")
    print("-" * 80)
    
    for category in ['Real Estate & Construction', 'Tourism & Hospitality', 'Economic & Financial']:
        result = db.execute(text("""
            SELECT COUNT(*) FROM data_sources WHERE category = :cat
        """), {'cat': category}).scalar()
        
        old = before.get(category, 0)
        change = result - old
        print(f"  {category:40} {old:>4} -> {result:>4} ({change:+d})")

def main():
    """Execute targeted improvement"""
    
    print("="*80)
    print("PHASE 1.5 TARGETED IMPROVEMENT")
    print("Focus: Fix Real Estate & Tourism under-representation")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Step 1: Audit before
        before = audit_before_state(db)
        
        # Step 2: Recategorize
        changes = recategorize_low_confidence(db)
        
        # Step 3: Audit after
        audit_after_state(db, before)
        
        print("\n" + "="*80)
        print("TARGETED IMPROVEMENT COMPLETE")
        print("="*80)
        print("\nNext: Phase 2 (ChromaDB embeddings + Agent integration)")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
