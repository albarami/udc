#!/usr/bin/env python3
"""
Create the udc_polaris database.
Run this before init_database.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# PostgreSQL connection settings
HOST = "localhost"
PORT = "5437"  # PostgreSQL 18
USER = "postgres"
PASSWORD = "112211"
DATABASE = "udc_polaris"

def create_database():
    """Create the udc_polaris database if it doesn't exist."""
    
    print("="*70)
    print("CREATING UDC POLARIS DATABASE")
    print("="*70)
    print()
    
    try:
        # Connect to default postgres database
        print("📡 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DATABASE,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{DATABASE}' already exists")
        else:
            # Create database
            print(f"🔨 Creating database '{DATABASE}'...")
            cursor.execute(f'CREATE DATABASE {DATABASE}')
            print(f"✅ Database '{DATABASE}' created successfully")
        
        cursor.close()
        conn.close()
        
        # Verify connection to new database
        print()
        print("🔍 Verifying connection to new database...")
        test_conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        test_conn.close()
        print("✅ Connection verified")
        
        print()
        print("="*70)
        print("✅ DATABASE CREATION COMPLETE")
        print("="*70)
        print()
        print("📊 Database Details:")
        print(f"   - Host: {HOST}")
        print(f"   - Port: {PORT}")
        print(f"   - Database: {DATABASE}")
        print(f"   - User: {USER}")
        print()
        print("🚀 Next Steps:")
        print("   1. Run: python scripts/init_database.py")
        print("   2. Run: python scripts/init_chromadb.py")
        print()
        
        return True
    
    except psycopg2.Error as e:
        print(f"\n❌ PostgreSQL Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check PostgreSQL service is running")
        print("2. Verify password is correct")
        print("3. Ensure port 5432 is not blocked")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = create_database()
    sys.exit(0 if success else 1)
