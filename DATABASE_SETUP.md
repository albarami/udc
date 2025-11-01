# Database Setup Guide - UDC Polaris

**Time Required:** 30-45 minutes  
**Databases:** PostgreSQL 15+ & ChromaDB  
**Status:** Ready to configure

---

## Overview

UDC Polaris uses two databases:
1. **PostgreSQL** - Structured data (sessions, agents, Qatar datasets)
2. **ChromaDB** - Vector embeddings (semantic search)

---

## Part 1: PostgreSQL Setup (20 minutes)

### Step 1: Install PostgreSQL

**Windows (Recommended):**
```powershell
# Download PostgreSQL 15 installer
# URL: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql15
```

**Verify installation:**
```powershell
psql --version
# Should show: psql (PostgreSQL) 15.x
```

---

### Step 2: Create Database

**Option A - Using pgAdmin (GUI):**
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `udc_polaris`
4. Owner: `postgres`
5. Click "Save"

**Option B - Using Command Line:**
```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE udc_polaris;

# Verify
\l

# Exit
\q
```

---

### Step 3: Configure Connection

**Update `backend/.env`:**
```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/udc_polaris
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=udc_polaris
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**Replace `your_password` with your PostgreSQL password!**

---

### Step 4: Create Tables

We'll use Alembic for migrations. First, install dependencies:

```powershell
cd backend
pip install alembic psycopg2-binary sqlalchemy
```

**Initialize database schema:**
```powershell
cd d:\udc
python scripts/init_database.py
```

This will create:
- `sessions` table - Analysis sessions
- `agents` table - Agent configurations
- `debates` table - Agent debate records
- `context_items` table - CEO context data
- `qatar_datasets` table - Metadata for Qatar datasets

---

### Step 5: Verify PostgreSQL Setup

```powershell
cd backend
python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('✅ PostgreSQL connected!'); db.close()"
```

---

## Part 2: ChromaDB Setup (15 minutes)

### Step 1: Install ChromaDB

```powershell
cd backend
pip install chromadb
```

---

### Step 2: Initialize ChromaDB

ChromaDB will store vector embeddings for semantic search of Qatar datasets.

**Run initialization:**
```powershell
cd d:\udc
python scripts/init_chromadb.py
```

This creates:
- `qatar_datasets` collection - Embeddings for all 1,149 datasets
- `documents` collection - Document chunks
- `analysis_history` collection - Past analyses

---

### Step 3: Configure ChromaDB Settings

**Update `backend/.env`:**
```bash
# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=../data/chromadb
CHROMA_COLLECTION_NAME=qatar_datasets
```

---

### Step 4: Verify ChromaDB Setup

```powershell
cd backend
python -c "import chromadb; client = chromadb.PersistentClient(path='../data/chromadb'); print('✅ ChromaDB connected!'); print(f'Collections: {client.list_collections()}')"
```

---

## Part 3: Data Ingestion (30 minutes)

Now that databases are ready, let's load the 1,149 Qatar datasets.

### Step 1: Ingest Qatar Datasets Metadata

```powershell
cd d:\udc
python scripts/ingest_qatar_metadata.py
```

This will:
- ✅ Load all 1,149 dataset metadata into PostgreSQL
- ✅ Create vector embeddings for semantic search
- ✅ Build search indices
- ✅ Generate data catalog

**Expected output:**
```
🔄 Ingesting Qatar datasets metadata...
✅ Loaded 1,149 datasets into PostgreSQL
✅ Created 1,149 vector embeddings in ChromaDB
✅ Built search indices
📊 Total records: 3,067,832
💾 Total size: 769.5 MB
```

---

### Step 2: Verify Data Ingestion

**Check PostgreSQL:**
```sql
psql -U postgres -d udc_polaris -c "SELECT COUNT(*) FROM qatar_datasets;"
-- Should return: 1149
```

**Check ChromaDB:**
```powershell
cd backend
python -c "import chromadb; client = chromadb.PersistentClient(path='../data/chromadb'); collection = client.get_collection('qatar_datasets'); print(f'✅ Vectors stored: {collection.count()}')"
-- Should return: 1149
```

---

## Part 4: Test Database Integration (10 minutes)

### Test 1: Query PostgreSQL

```powershell
cd d:\udc
python scripts/test_postgres_query.py
```

**Sample queries:**
- Find all real estate datasets
- Get Gewan Island data
- Query Qatar Cool statistics

---

### Test 2: Test Semantic Search

```powershell
cd d:\udc
python scripts/test_chromadb_search.py
```

**Sample searches:**
- "hotel occupancy rates"
- "real estate transactions"
- "energy consumption"

---

## Troubleshooting

### PostgreSQL Issues

**Error: "password authentication failed"**
```powershell
# Reset password
psql -U postgres
ALTER USER postgres PASSWORD 'new_password';
\q

# Update backend/.env with new password
```

**Error: "database does not exist"**
```powershell
psql -U postgres
CREATE DATABASE udc_polaris;
\q
```

**Error: "could not connect to server"**
```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*

# If not running:
Start-Service postgresql-x64-15
```

---

### ChromaDB Issues

**Error: "No module named 'chromadb'"**
```powershell
cd backend
pip install chromadb
```

**Error: "Collection not found"**
```powershell
# Re-run initialization
cd d:\udc
python scripts/init_chromadb.py
```

---

## Next Steps After Setup

Once both databases are configured:

1. ✅ **Test Dr. Omar with Database** - Real queries against PostgreSQL
2. ✅ **Implement Dr. James (CFO)** - Financial analysis agent
3. ✅ **Build Context Gathering** - Interactive CEO questioning
4. ✅ **Session Management** - Track analysis sessions

---

## Configuration Summary

**Backend `.env` should have:**
```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/udc_polaris
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=udc_polaris
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ChromaDB
CHROMA_PERSIST_DIRECTORY=../data/chromadb
CHROMA_COLLECTION_NAME=qatar_datasets
```

---

## Verification Checklist

Before proceeding to Week 3-4 tasks:

- [ ] PostgreSQL installed and running
- [ ] Database `udc_polaris` created
- [ ] Tables created successfully
- [ ] PostgreSQL connection test passes
- [ ] ChromaDB installed
- [ ] ChromaDB collections initialized
- [ ] ChromaDB connection test passes
- [ ] Qatar datasets metadata ingested (1,149 datasets)
- [ ] Vector embeddings created (1,149 vectors)
- [ ] Sample queries working

---

**Status:** Ready to configure  
**Next:** Run `python scripts/init_database.py` to start setup

---

**Created:** October 31, 2025  
**For:** UDC Polaris Week 3-4 Infrastructure Setup
