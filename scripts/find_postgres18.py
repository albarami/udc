#!/usr/bin/env python3
"""
Find which port PostgreSQL 18 is running on.
"""

import psycopg2

PASSWORD = "112211"
PORTS_TO_TRY = [5432, 5433, 5434, 5435, 5436, 5437, 5438]

print("="*70)
print("FINDING POSTGRESQL 18 INSTANCE")
print("="*70)
print()

for port in PORTS_TO_TRY:
    try:
        print(f"🔍 Trying port {port}...", end=" ")
        conn = psycopg2.connect(
            host="localhost",
            port=port,
            user="postgres",
            password=PASSWORD,
            database="postgres",
            connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ FOUND!")
        print(f"   Version: {version}")
        
        if "PostgreSQL 18" in version:
            print()
            print("="*70)
            print(f"✅ POSTGRESQL 18 FOUND ON PORT {port}")
            print("="*70)
            print()
            print(f"Use this connection string:")
            print(f"postgresql://postgres:{PASSWORD}@localhost:{port}/udc_polaris")
            print()
            
            # Save to file
            with open("postgres18_port.txt", "w") as f:
                f.write(str(port))
            print(f"Saved port to: postgres18_port.txt")
            break
        else:
            print(f"   (Different version)")
    
    except psycopg2.OperationalError:
        print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("="*70)
