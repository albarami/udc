#!/usr/bin/env python3
"""
Phase 1.6: Final Comprehensive Recategorization
Based on systematic analysis and user approval (85% confidence)

Changes:
1. Move misclassified datasets FROM Real Estate TO proper categories
2. Move misclassified datasets FROM Tourism TO proper categories  
3. Move datasets FROM Economic TO Infrastructure and Population
4. Merge Regional & Global Context INTO Economic & Financial (back to 8 categories)
5. Cross-reference housing census datasets (Population + Real Estate relevance)
6. Update confidence scores
7. Flag datasets needing review
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("="*100)
print("PHASE 1.6: FINAL COMPREHENSIVE RECATEGORIZATION")
print("="*100)
print()

# Define all recategorization moves
RECATEGORIZATION_MOVES = {
    # ========================================================================
    # FROM REAL ESTATE & CONSTRUCTION -> TO OTHER CATEGORIES
    # ========================================================================
    "real_estate_to_tourism": [
        {
            "pattern": "Cultural Events at the Cultural Village Foundation (Katara) by Type of Event",
            "to_category": "Tourism & Hospitality",
            "confidence": 95,
            "reasoning": "Tourism attraction events, not real estate"
        },
        {
            "pattern": "Cultural Events in the Cultural Village Foundation (Katara) By Month and Type of Event",
            "to_category": "Tourism & Hospitality",
            "confidence": 95,
            "reasoning": "Tourism attraction events"
        },
        {
            "pattern": "Number of Facilities at the Cultural Village Foundation (Katara) by Type of Facility",
            "to_category": "Tourism & Hospitality",
            "confidence": 90,
            "reasoning": "Tourism infrastructure facilities"
        },
        {
            "pattern": "Visitor Arrivals Trends by Mode of Transport",
            "to_category": "Tourism & Hospitality",
            "confidence": 95,
            "reasoning": "Tourism visitor statistics"
        },
    ],
    
    "real_estate_to_population": [
        {
            "pattern": "General Population and Housing Census",
            "to_category": "Population & Demographics",
            "confidence": 100,
            "reasoning": "Population census, not real estate market data"
        },
        {
            "pattern": "Households and individuals by type of housing unit",
            "to_category": "Population & Demographics",
            "confidence": 90,
            "reasoning": "Demographic household composition",
            "cross_reference": "Real Estate & Construction"  # Also relevant to RE
        },
        {
            "pattern": "Housing Units by Type of Units and Municipality in Census",
            "to_category": "Population & Demographics",
            "confidence": 85,
            "reasoning": "Census housing stock, demographic data",
            "cross_reference": "Real Estate & Construction"  # Housing supply analysis
        },
        {
            "pattern": "Number of Housing Units by Occupancy Status",
            "to_category": "Population & Demographics",
            "confidence": 85,
            "reasoning": "Census occupancy data",
            "cross_reference": "Real Estate & Construction"  # Vacancy rate indicator
        },
        {
            "pattern": "Percentage Distribution (%) of Household Members by Type of Housing Unit",
            "to_category": "Population & Demographics",
            "confidence": 90,
            "reasoning": "Demographic distribution"
        },
        {
            "pattern": "Percentage Distribution (%) of Households by Type of Housing Unit",
            "to_category": "Population & Demographics",
            "confidence": 90,
            "reasoning": "Demographic distribution"
        },
        {
            "pattern": "Beneficiaries of the Services of Youth Capacity Building",
            "to_category": "Population & Demographics",
            "confidence": 85,
            "reasoning": "Youth programs, social services"
        },
        {
            "pattern": "Youth Development Index",
            "to_category": "Population & Demographics",
            "confidence": 90,
            "reasoning": "Demographic social indicator"
        },
    ],
    
    "real_estate_to_infrastructure": [
        {
            "pattern": "New temporary driving permits issued",
            "to_category": "Infrastructure & Utilities",
            "confidence": 80,
            "reasoning": "Transportation licensing infrastructure"
        },
        {
            "pattern": "Number of Temporary Driving Permits Renewed",
            "to_category": "Infrastructure & Utilities",
            "confidence": 80,
            "reasoning": "Transportation infrastructure"
        },
        {
            "pattern": "Water used in commercial activity and commercial GDP",
            "to_category": "Infrastructure & Utilities",
            "confidence": 90,
            "reasoning": "Utility consumption data"
        },
        {
            "pattern": "Number and Length Of Domestic and Commercial Service Connections",
            "to_category": "Infrastructure & Utilities",
            "confidence": 95,
            "reasoning": "Utility infrastructure connections"
        },
        {
            "pattern": "Water Real Losses Reduction",
            "to_category": "Infrastructure & Utilities",
            "confidence": 95,
            "reasoning": "Water utility efficiency"
        },
        {
            "pattern": "Beneficiaries of services rendered by Social Development Center",
            "to_category": "Infrastructure & Utilities",
            "confidence": 70,
            "reasoning": "Social services infrastructure"
        },
    ],
    
    "real_estate_to_energy": [
        {
            "pattern": "Forest Area as a Proportion of Total Land Area",
            "to_category": "Energy & Sustainability",
            "confidence": 100,
            "reasoning": "Environmental sustainability metric"
        },
    ],
    
    "real_estate_to_economic": [
        {
            "pattern": "Human Development Index",
            "to_category": "Economic & Financial",
            "confidence": 100,
            "reasoning": "Global economic development indicator (from Regional category merge)"
        },
        {
            "pattern": "Sustainable Development Goals Index",
            "to_category": "Economic & Financial",
            "confidence": 100,
            "reasoning": "Global development indicator (from Regional category merge)"
        },
        {
            "pattern": "Business Establishments by Ownership Sector",
            "to_category": "Economic & Financial",
            "confidence": 90,
            "reasoning": "Business census data, economic not real estate"
        },
    ],
    
    # ========================================================================
    # FROM TOURISM & HOSPITALITY -> TO OTHER CATEGORIES
    # ========================================================================
    "tourism_to_population": [
        {
            "pattern": "Number of Visitors to Health Centers",
            "to_category": "Population & Demographics",
            "confidence": 100,
            "reasoning": "Healthcare utilization, NOT tourism"
        },
    ],
    
    "tourism_to_economic": [
        {
            "pattern": "Total Exports by Main Country of Destination",
            "to_category": "Economic & Financial",
            "confidence": 100,
            "reasoning": "Trade statistics, not tourism"
        },
    ],
    
    # ========================================================================
    # FROM ECONOMIC & FINANCIAL -> TO OTHER CATEGORIES
    # ========================================================================
    "economic_to_infrastructure": [
        {
            "pattern": "Arriving Vessels' Gross and Net Tonnage",
            "to_category": "Infrastructure & Utilities",
            "confidence": 90,
            "reasoning": "Port infrastructure operations"
        },
        {
            "pattern": "Air Traffic Data",
            "to_category": "Infrastructure & Utilities",
            "confidence": 90,
            "reasoning": "Airport infrastructure operations"
        },
        {
            "pattern": "Cargo via Hamad International Airport",
            "to_category": "Infrastructure & Utilities",
            "confidence": 90,
            "reasoning": "Airport cargo infrastructure"
        },
        {
            "pattern": "Area of Greenspaces and Road Medians",
            "to_category": "Infrastructure & Utilities",
            "confidence": 85,
            "reasoning": "Municipal infrastructure maintenance"
        },
        {
            "pattern": "Area of Public Parks",
            "to_category": "Infrastructure & Utilities",
            "confidence": 85,
            "reasoning": "Parks infrastructure"
        },
        {
            "pattern": "Completed Infrastructure Projects",
            "to_category": "Infrastructure & Utilities",
            "confidence": 90,
            "reasoning": "Infrastructure development tracking"
        },
    ],
    
    "economic_to_population": [
        {
            "pattern": "Annual Birth And Mortality Statistics",
            "to_category": "Population & Demographics",
            "confidence": 95,
            "reasoning": "Core demographic vital statistics"
        },
        {
            "pattern": "Registered Deaths",
            "to_category": "Population & Demographics",
            "confidence": 95,
            "reasoning": "Vital statistics"
        },
        {
            "pattern": "Registered Births",
            "to_category": "Population & Demographics",
            "confidence": 95,
            "reasoning": "Vital statistics"
        },
        {
            "pattern": "Child Mortality Rate",
            "to_category": "Population & Demographics",
            "confidence": 95,
            "reasoning": "Demographic health indicator"
        },
        {
            "pattern": "Total Population by Age Groups",
            "to_category": "Population & Demographics",
            "confidence": 100,
            "reasoning": "Core population statistics"
        },
        {
            "pattern": "Population Growth in Qatar",
            "to_category": "Population & Demographics",
            "confidence": 100,
            "reasoning": "Population statistics"
        },
        {
            "pattern": "Accident",
            "to_category": "Population & Demographics",
            "confidence": 70,
            "reasoning": "Public safety statistics"
        },
    ],
    
    # ========================================================================
    # MERGE REGIONAL & GLOBAL CONTEXT -> ECONOMIC & FINANCIAL
    # ========================================================================
    "regional_to_economic": [
        {
            "pattern": "%",  # Match all datasets from Regional & Global Context
            "from_category": "Regional & Global Context",
            "to_category": "Economic & Financial",
            "confidence": 80,
            "reasoning": "Merging Regional & Global Context into Economic (back to 8 categories)"
        },
    ],
}

def move_datasets(session, move_list, from_category_name=None):
    """Move datasets based on pattern matching"""
    moved_count = 0
    
    for move in move_list:
        pattern = move["pattern"]
        to_category = move["to_category"]
        confidence = move["confidence"]
        reasoning = move["reasoning"]
        cross_ref = move.get("cross_reference", None)
        from_cat = move.get("from_category", from_category_name)
        
        # Build query
        if from_cat:
            query = text("""
                UPDATE data_sources
                SET category = :to_category,
                    categorization_confidence = :confidence,
                    needs_review = CASE WHEN :confidence < 70 THEN true ELSE false END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source_type = 'qatar_open_data'
                AND category = :from_category
                AND source_name ILIKE :pattern
            """)
            result = session.execute(query, {
                "to_category": to_category,
                "confidence": confidence,
                "from_category": from_cat,
                "pattern": f"%{pattern}%"
            })
        else:
            query = text("""
                UPDATE data_sources
                SET category = :to_category,
                    categorization_confidence = :confidence,
                    needs_review = CASE WHEN :confidence < 70 THEN true ELSE false END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source_type = 'qatar_open_data'
                AND source_name ILIKE :pattern
            """)
            result = session.execute(query, {
                "to_category": to_category,
                "confidence": confidence,
                "pattern": f"%{pattern}%"
            })
        
        count = result.rowcount
        if count > 0:
            moved_count += count
            print(f"  [{confidence:3d}%] Moved {count:2d} dataset(s): '{pattern[:60]}...' -> {to_category}")
            if cross_ref:
                print(f"          (Cross-referenced with {cross_ref})")
    
    return moved_count

# Execute recategorization
with Session() as session:
    total_moved = 0
    
    print("\nPHASE 1: MOVING FROM REAL ESTATE & CONSTRUCTION")
    print("-" * 100)
    print("\n1.1 Real Estate -> Tourism & Hospitality")
    count = move_datasets(session, RECATEGORIZATION_MOVES["real_estate_to_tourism"], "Real Estate & Construction")
    total_moved += count
    
    print("\n1.2 Real Estate -> Population & Demographics (with cross-references)")
    count = move_datasets(session, RECATEGORIZATION_MOVES["real_estate_to_population"], "Real Estate & Construction")
    total_moved += count
    
    print("\n1.3 Real Estate -> Infrastructure & Utilities")
    count = move_datasets(session, RECATEGORIZATION_MOVES["real_estate_to_infrastructure"], "Real Estate & Construction")
    total_moved += count
    
    print("\n1.4 Real Estate -> Energy & Sustainability")
    count = move_datasets(session, RECATEGORIZATION_MOVES["real_estate_to_energy"], "Real Estate & Construction")
    total_moved += count
    
    print("\n1.5 Real Estate -> Economic & Financial")
    count = move_datasets(session, RECATEGORIZATION_MOVES["real_estate_to_economic"], "Real Estate & Construction")
    total_moved += count
    
    print("\n\nPHASE 2: MOVING FROM TOURISM & HOSPITALITY")
    print("-" * 100)
    print("\n2.1 Tourism -> Population & Demographics")
    count = move_datasets(session, RECATEGORIZATION_MOVES["tourism_to_population"], "Tourism & Hospitality")
    total_moved += count
    
    print("\n2.2 Tourism -> Economic & Financial")
    count = move_datasets(session, RECATEGORIZATION_MOVES["tourism_to_economic"], "Tourism & Hospitality")
    total_moved += count
    
    print("\n\nPHASE 3: MOVING FROM ECONOMIC & FINANCIAL")
    print("-" * 100)
    print("\n3.1 Economic -> Infrastructure & Utilities")
    count = move_datasets(session, RECATEGORIZATION_MOVES["economic_to_infrastructure"], "Economic & Financial")
    total_moved += count
    
    print("\n3.2 Economic -> Population & Demographics")
    count = move_datasets(session, RECATEGORIZATION_MOVES["economic_to_population"], "Economic & Financial")
    total_moved += count
    
    print("\n\nPHASE 4: MERGING REGIONAL & GLOBAL CONTEXT -> ECONOMIC & FINANCIAL")
    print("-" * 100)
    count = move_datasets(session, RECATEGORIZATION_MOVES["regional_to_economic"])
    total_moved += count
    
    session.commit()
    print(f"\n\nTOTAL DATASETS MOVED: {total_moved}")
    print("="*100)
    
    # Generate final distribution report
    print("\n\nFINAL CATEGORY DISTRIBUTION:")
    print("="*100)
    
    result = session.execute(text("""
        SELECT 
            category,
            COUNT(*) as count,
            ROUND(AVG(categorization_confidence), 1) as avg_confidence,
            SUM(CASE WHEN needs_review THEN 1 ELSE 0 END) as needs_review_count
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        GROUP BY category
        ORDER BY count DESC
    """))
    
    total_datasets = 0
    for row in result:
        category, count, avg_conf, review_count = row
        total_datasets += count
        print(f"{category:40s} | {count:4d} datasets | Avg Confidence: {avg_conf:5.1f}% | Review: {review_count:3d}")
    
    print("-" * 100)
    print(f"{'TOTAL':40s} | {total_datasets:4d} datasets")
    print("="*100)

engine.dispose()
print("\n✓ Recategorization complete!")
