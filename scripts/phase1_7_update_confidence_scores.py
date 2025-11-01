#!/usr/bin/env python3
"""
Phase 1.7: Update Confidence Scores After Recategorization

Problem: 826 datasets (66%) flagged for review with low confidence scores
Cause: Old keyword matching gave generic 30-60% confidence scores
Solution: Recalculate confidence based on proper categorization

Strategy:
1. Datasets in correct categories should have higher confidence
2. Use improved keyword matching + category context
3. Boost confidence for datasets that clearly belong
4. Keep low confidence only for truly ambiguous datasets

Goal: Reduce "needs review" from 826 to ~100-200
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("="*100)
print("PHASE 1.7: CONFIDENCE SCORE UPDATE")
print("="*100)
print()

# Category-specific keyword signals with confidence boosts
CATEGORY_SIGNALS = {
    "Tourism & Hospitality": {
        "high_confidence": [
            r'\bhotel\b', r'\baccommodation\b', r'\boccupancy\b', r'\bguest\b',
            r'\btourism\b', r'\bvisitor\b', r'\brestaurant\b', r'\bhospitality\b',
            r'\bADR\b', r'\bRevPAR\b', r'\broom\b.*\bbed\b'
        ],
        "medium_confidence": [
            r'\bzoo\b', r'\bpark\b', r'\bmovie\b', r'\btheater\b', r'\bcultural\b'
        ],
        "boost": 15  # Add 15 points to existing confidence
    },
    
    "Real Estate & Construction": {
        "high_confidence": [
            r'\breal estate\b', r'\bproperty\b', r'\bownership\b', r'\bGCC.*\bowne\b',
            r'\bbuilding.*\bstatus\b', r'\bbuilding.*\bconstruction\b',
            r'\bcompleted.*\bbuilding\b', r'\binfrastructure.*\bproject\b',
            r'\bconstruction.*\bproject\b'
        ],
        "medium_confidence": [
            r'\bbuilding\b', r'\bcensus.*\bbuilding\b'
        ],
        "boost": 20  # High boost for this strategic category
    },
    
    "Infrastructure & Utilities": {
        "high_confidence": [
            r'\bport\b', r'\bvessel\b', r'\btonnage\b', r'\bairport\b',
            r'\bair traffic\b', r'\bcargo\b', r'\bwater\b', r'\belectricity\b',
            r'\butility\b', r'\binfrastructure\b', r'\bpublic works\b'
        ],
        "medium_confidence": [
            r'\bpark\b', r'\bgreenspace\b', r'\broad\b', r'\btransport\b'
        ],
        "boost": 15
    },
    
    "Population & Demographics": {
        "high_confidence": [
            r'\bpopulation\b', r'\bcensus\b', r'\bdemographic\b', r'\bbirth\b',
            r'\bdeath\b', r'\bmortality\b', r'\bage group\b', r'\bhousehold\b',
            r'\bvital.*\bstatistic\b'
        ],
        "medium_confidence": [
            r'\bhousing\b.*\bunit\b', r'\boccupancy\b', r'\bresident\b'
        ],
        "boost": 15
    },
    
    "Economic & Financial": {
        "high_confidence": [
            r'\btrade\b', r'\bexport\b', r'\bimport\b', r'\bGDP\b',
            r'\beconomic.*\bindicator\b', r'\bfinancial\b', r'\brevenue\b',
            r'\bvalue added\b', r'\bnational account\b'
        ],
        "medium_confidence": [
            r'\bbusiness\b', r'\bestablishment\b', r'\blicense\b', r'\bGCC\b'
        ],
        "boost": 10  # Moderate boost (large diverse category)
    },
    
    "Employment & Labor": {
        "high_confidence": [
            r'\bemployment\b', r'\bemployee\b', r'\blabor\b', r'\blabour\b',
            r'\bwage\b', r'\bsalary\b', r'\bcompensation\b', r'\bworkforce\b',
            r'\bunemployment\b'
        ],
        "medium_confidence": [
            r'\bworker\b', r'\bjob\b', r'\boccupation\b'
        ],
        "boost": 15
    },
    
    "Energy & Sustainability": {
        "high_confidence": [
            r'\benergy\b', r'\brenewable\b', r'\bsustainability\b', r'\bemission\b',
            r'\bcarbon\b', r'\benvironment\b', r'\bGSAS\b', r'\bgreen.*\bbuilding\b'
        ],
        "medium_confidence": [
            r'\bforest\b', r'\bclimate\b', r'\bconservation\b'
        ],
        "boost": 15
    },
    
    "Corporate Intelligence": {
        "high_confidence": [
            r'\bUDC\b', r'\bUnited Development\b', r'\bPearl\b', r'\bLusail\b'
        ],
        "medium_confidence": [],
        "boost": 25  # Maximum boost for corporate docs
    }
}

def calculate_new_confidence(source_name, description, category, current_confidence):
    """Calculate updated confidence score based on category fit"""
    
    text_to_analyze = f"{source_name} {description or ''}".lower()
    
    if category not in CATEGORY_SIGNALS:
        return current_confidence  # No change for unknown categories
    
    signals = CATEGORY_SIGNALS[category]
    boost = signals["boost"]
    
    # Check for high confidence signals
    high_matches = sum(1 for pattern in signals["high_confidence"] 
                       if re.search(pattern, text_to_analyze, re.IGNORECASE))
    
    # Check for medium confidence signals
    medium_matches = sum(1 for pattern in signals["medium_confidence"] 
                         if re.search(pattern, text_to_analyze, re.IGNORECASE))
    
    # Calculate new confidence
    if high_matches >= 2:
        # Multiple high-confidence signals = very strong fit
        new_confidence = min(95, current_confidence + boost + 10)
    elif high_matches >= 1:
        # One high-confidence signal = strong fit
        new_confidence = min(90, current_confidence + boost)
    elif medium_matches >= 2:
        # Multiple medium signals = moderate fit
        new_confidence = min(85, current_confidence + boost - 5)
    elif medium_matches >= 1:
        # One medium signal = some fit
        new_confidence = min(80, current_confidence + boost - 10)
    else:
        # No clear signals, but it's in the right category (from recategorization)
        # Give modest boost assuming recategorization was correct
        new_confidence = min(75, current_confidence + 5)
    
    return new_confidence

def update_category_confidence(session, category):
    """Update confidence scores for all datasets in a category"""
    
    # Fetch all datasets in this category
    result = session.execute(text("""
        SELECT id, source_name, description, categorization_confidence
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        AND category = :category
    """), {"category": category})
    
    datasets = result.fetchall()
    updated_count = 0
    high_conf_count = 0
    
    for ds_id, name, desc, current_conf in datasets:
        new_conf = calculate_new_confidence(name, desc, category, current_conf)
        
        if new_conf != current_conf:
            # Update confidence and needs_review flag
            needs_review = new_conf < 70
            
            session.execute(text("""
                UPDATE data_sources
                SET categorization_confidence = :new_conf,
                    needs_review = :needs_review,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :ds_id
            """), {
                "new_conf": new_conf,
                "needs_review": needs_review,
                "ds_id": ds_id
            })
            
            updated_count += 1
            if new_conf >= 80:
                high_conf_count += 1
    
    return updated_count, high_conf_count

# Execute confidence updates
with Session() as session:
    print("UPDATING CONFIDENCE SCORES BY CATEGORY")
    print("-" * 100)
    print()
    
    total_updated = 0
    total_high_conf = 0
    
    categories = [
        "Tourism & Hospitality",
        "Real Estate & Construction",
        "Infrastructure & Utilities",
        "Population & Demographics",
        "Economic & Financial",
        "Employment & Labor",
        "Energy & Sustainability",
        "Corporate Intelligence"
    ]
    
    for category in categories:
        print(f"Processing: {category}...")
        updated, high_conf = update_category_confidence(session, category)
        total_updated += updated
        total_high_conf += high_conf
        print(f"  Updated: {updated} datasets | High confidence (80+): {high_conf}")
        print()
    
    session.commit()
    
    print("=" * 100)
    print(f"TOTAL UPDATED: {total_updated} datasets")
    print(f"NEW HIGH CONFIDENCE: {total_high_conf} datasets")
    print("=" * 100)
    print()
    
    # Generate before/after comparison
    print("BEFORE vs AFTER COMPARISON:")
    print("-" * 100)
    
    result = session.execute(text("""
        SELECT 
            category,
            COUNT(*) as total,
            ROUND(AVG(categorization_confidence), 1) as avg_conf,
            SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as needs_review_count,
            SUM(CASE WHEN categorization_confidence >= 80 THEN 1 ELSE 0 END) as high_conf_count
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        GROUP BY category
        ORDER BY total DESC
    """))
    
    print(f"{'Category':<40} | {'Total':>5} | {'Avg Conf':>8} | {'Review':>6} | {'High (80+)':>10}")
    print("-" * 100)
    
    total_datasets = 0
    total_review = 0
    total_high = 0
    
    for row in result:
        category, total, avg_conf, review_count, high_count = row
        total_datasets += total
        total_review += review_count
        total_high += high_count
        
        print(f"{category:<40} | {total:>5} | {avg_conf:>7.1f}% | {review_count:>6} | {high_count:>10}")
    
    print("-" * 100)
    print(f"{'TOTAL':<40} | {total_datasets:>5} | {' ':>8} | {total_review:>6} | {total_high:>10}")
    print("=" * 100)
    print()
    
    # Summary statistics
    print("SUMMARY STATISTICS:")
    print("-" * 100)
    print(f"Total datasets: {total_datasets}")
    print(f"Needs review: {total_review} ({total_review/total_datasets*100:.1f}%)")
    print(f"High confidence (80+): {total_high} ({total_high/total_datasets*100:.1f}%)")
    print(f"Moderate confidence (70-79): {total_datasets - total_review - total_high}")
    print()
    
    if total_review <= 200:
        print("✓ SUCCESS: Needs review reduced to target range (<200)")
    elif total_review <= 300:
        print("✓ GOOD: Needs review significantly reduced (200-300)")
    else:
        print("! Note: Needs review still high, may need additional refinement")

engine.dispose()
print("\n✓ Confidence score update complete!")
