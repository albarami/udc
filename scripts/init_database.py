#!/usr/bin/env python3
"""
Initialize PostgreSQL database for UDC Polaris.
Creates all required tables and indexes.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from app.db.models import Base, AnalysisSession, CEOContext, AgentResponse, DebateTension, DataSource, TokenUsageLog

# Database URL (hardcoded for initialization)
DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"

def init_database():
    """Initialize the database with all tables."""
    
    print("="*70)
    print("UDC POLARIS - DATABASE INITIALIZATION")
    print("="*70)
    print()
    
    try:
        # Create engine
        print("📡 Connecting to PostgreSQL...")
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
        
        print()
        print("🔨 Creating tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
        
        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Create indexes for performance
        print()
        print("🔍 Creating indexes...")
        
        with engine.connect() as conn:
            # Index on analysis session status for fast filtering
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analysis_sessions_status 
                ON analysis_sessions(session_status)
            """))
            
            # Index on analysis session created_at for sorting
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created 
                ON analysis_sessions(created_at DESC)
            """))
            
            # Index on data_sources category
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_data_sources_category 
                ON data_sources(category)
            """))
            
            conn.commit()
        
        print("✅ Created performance indexes")
        
        # Agent configurations will be defined in code (not in database table for MVP)
        print()
        print("✅ Agent configurations will be managed in code")
        
        # Summary
        print()
        print("="*70)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("="*70)
        print()
        print("📊 Database Status:")
        print(f"   - Database: udc_polaris")
        print(f"   - Tables: {len(tables)}")
        print(f"   - Indexes: 3 performance indexes")
        print(f"   - Agents: Managed in code")
        print()
        print("🚀 Next Steps:")
        print("   1. Run: python scripts/init_chromadb.py")
        print("   2. Run: python scripts/ingest_qatar_metadata.py")
        print("   3. Test: python scripts/test_postgres_query.py")
        print()
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check PostgreSQL is running: Get-Service postgresql*")
        print("2. Verify credentials in backend/.env")
        print("3. Ensure database 'udc_polaris' exists")
        print("4. Check DATABASE_URL format")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
