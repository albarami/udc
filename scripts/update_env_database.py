#!/usr/bin/env python3
"""
Update backend/.env with database credentials.
"""

from pathlib import Path

# Database credentials
DB_HOST = "localhost"
DB_PORT = "5437"  # PostgreSQL 18
DB_USER = "postgres"
DB_PASSWORD = "112211"
DB_NAME = "udc_polaris"

# Construct DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def update_env():
    """Update or add database settings to .env file."""
    
    env_path = Path(__file__).parent.parent / "backend" / ".env"
    
    print("="*70)
    print("UPDATING BACKEND/.ENV WITH DATABASE SETTINGS")
    print("="*70)
    print()
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Database settings to add/update
    db_settings = {
        "DATABASE_URL": DATABASE_URL,
        "POSTGRES_HOST": DB_HOST,
        "POSTGRES_PORT": DB_PORT,
        "POSTGRES_USER": DB_USER,
        "POSTGRES_PASSWORD": DB_PASSWORD,
        "POSTGRES_DB": DB_NAME,
    }
    
    # Track which settings we've updated
    updated = set()
    new_lines = []
    
    # Update existing lines
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and not line_stripped.startswith('#'):
            key = line_stripped.split('=')[0]
            if key in db_settings:
                new_lines.append(f"{key}={db_settings[key]}\n")
                updated.add(key)
                print(f"✅ Updated: {key}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add new settings that weren't in the file
    if updated != set(db_settings.keys()):
        new_lines.append("\n# PostgreSQL Database Configuration\n")
        for key, value in db_settings.items():
            if key not in updated:
                new_lines.append(f"{key}={value}\n")
                print(f"✅ Added: {key}")
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print()
    print("="*70)
    print("✅ BACKEND/.ENV UPDATED")
    print("="*70)
    print()
    print("📊 Database Configuration:")
    print(f"   - Host: {DB_HOST}")
    print(f"   - Port: {DB_PORT}")
    print(f"   - Database: {DB_NAME}")
    print(f"   - User: {DB_USER}")
    print(f"   - URL: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()


if __name__ == "__main__":
    update_env()
