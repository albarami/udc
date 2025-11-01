#!/usr/bin/env python3
"""
Seed database with 9-category structure.
Aligned with UDC's strategic priorities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import psycopg2
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"

# 9 Strategic Categories with Priorities
CATEGORIES = [
    {
        'category_name': 'Real Estate & Construction',
        'description': 'Property data, construction permits, real estate transactions, occupancy rates',
        'keywords': ['property', 'real estate', 'construction', 'building', 'occupancy', 'rental', 'land'],
        'priority': 10,  # Critical
        'color': '#FF0000'
    },
    {
        'category_name': 'Tourism & Hospitality',
        'description': 'Hotel statistics, tourist arrivals, hospitality sector performance',
        'keywords': ['tourism', 'hotel', 'visitor', 'hospitality', 'accommodation', 'travel', 'tourist'],
        'priority': 10,  # Critical
        'color': '#FF4444'
    },
    {
        'category_name': 'Infrastructure & Utilities',
        'description': 'Ports, water, power, roads, district cooling, public infrastructure',
        'keywords': ['infrastructure', 'utilities', 'cooling', 'electricity', 'water', 'transport', 'port', 'power'],
        'priority': 10,  # Critical
        'color': '#FF8800'
    },
    {
        'category_name': 'Economic & Financial',
        'description': 'Market conditions, GDP, investment climate, inflation, financial indicators',
        'keywords': ['economic', 'gdp', 'inflation', 'financial', 'market', 'investment', 'economy'],
        'priority': 9,  # High
        'color': '#FFAA00'
    },
    {
        'category_name': 'Energy & Sustainability',
        'description': 'Energy consumption, renewable energy, emissions, climate, ESG metrics',
        'keywords': ['energy', 'sustainability', 'renewable', 'emissions', 'climate', 'esg', 'environment'],
        'priority': 9,  # High
        'color': '#00AA00'
    },
    {
        'category_name': 'Population & Demographics',
        'description': 'Population data, demographics, migration, household composition, demand forecasting',
        'keywords': ['population', 'demographic', 'census', 'migration', 'residents', 'household'],
        'priority': 7,  # Medium
        'color': '#0088FF'
    },
    {
        'category_name': 'Employment & Labor',
        'description': 'Employment statistics, wages, labor market, Qatarization, workforce planning',
        'keywords': ['employment', 'labor', 'wage', 'salary', 'workforce', 'jobs', 'qatarization'],
        'priority': 7,  # Medium
        'color': '#8800FF'
    },
    {
        'category_name': 'Corporate Intelligence',
        'description': 'UDC financials, annual reports, competitor analysis, internal documents',
        'keywords': ['udc', 'annual report', 'financial statement', 'investor', 'corporate', 'quarterly'],
        'priority': 10,  # Critical
        'color': '#FFD700'
    },
    {
        'category_name': 'Regional & Global Context',
        'description': 'GCC benchmarking, World Bank data, IMF indicators, UN statistics, regional trends',
        'keywords': ['gcc', 'world bank', 'imf', 'un', 'regional', 'international', 'benchmark', 'global'],
        'priority': 9,  # High
        'color': '#00DDDD'
    }
]

def seed_categories():
    """Seed database with strategic categories."""
    
    print("="*70)
    print("SEEDING 9 STRATEGIC CATEGORIES")
    print("="*70)
    print()
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Create category tracking table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_categories (
            id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            keywords TEXT[],
            priority INTEGER DEFAULT 5,
            color VARCHAR(7),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    
    # Clear existing categories
    cursor.execute("DELETE FROM data_categories")
    conn.commit()
    
    # Insert new categories
    print("📂 Inserting categories:")
    print("-" * 70)
    
    for cat in CATEGORIES:
        cursor.execute("""
            INSERT INTO data_categories 
            (category_name, description, keywords, priority, color)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            cat['category_name'],
            cat['description'],
            cat['keywords'],
            cat['priority'],
            cat['color']
        ))
        
        priority_label = {10: '🔴 Critical', 9: '🟡 High', 7: '🟢 Medium'}.get(cat['priority'], '⚪ Low')
        print(f"{cat['category_name']:35} {priority_label}")
    
    conn.commit()
    
    print()
    print("="*70)
    print("✅ CATEGORIES SEEDED SUCCESSFULLY")
    print("="*70)
    print()
    print(f"Total categories: {len(CATEGORIES)}")
    print(f"Critical priority: {sum(1 for c in CATEGORIES if c['priority'] == 10)}")
    print(f"High priority: {sum(1 for c in CATEGORIES if c['priority'] == 9)}")
    print(f"Medium priority: {sum(1 for c in CATEGORIES if c['priority'] == 7)}")
    print()
    
    cursor.close()
    conn.close()
    
    return True


if __name__ == "__main__":
    seed_categories()
