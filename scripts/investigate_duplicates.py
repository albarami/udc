#!/usr/bin/env python3
"""
Investigate duplicate datasets in ChromaDB
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import chromadb
from chromadb.config import Settings

CHROMADB_PATH = str(Path(__file__).parent.parent / 'chromadb_data')

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(
    path=CHROMADB_PATH,
    settings=Settings(anonymized_telemetry=False)
)

qatar_collection = chroma_client.get_collection("qatar_open_data")

print("="*100)
print("INVESTIGATING DUPLICATE DATASETS IN CHROMADB")
print("="*100)
print()

# Get all datasets
all_data = qatar_collection.get()

print(f"Total datasets in ChromaDB: {len(all_data['ids'])}")
print()

# Check for duplicate IDs
id_counts = {}
for dataset_id in all_data['ids']:
    id_counts[dataset_id] = id_counts.get(dataset_id, 0) + 1

duplicates = {id: count for id, count in id_counts.items() if count > 1}

if duplicates:
    print(f"❌ FOUND {len(duplicates)} DUPLICATE IDs:")
    print("-" * 100)
    for dup_id, count in list(duplicates.items())[:10]:
        print(f"  ID: {dup_id} appears {count} times")
else:
    print("✅ No duplicate IDs found in ChromaDB")

print()

# Check for duplicate titles
title_to_ids = {}
for i, metadata in enumerate(all_data['metadatas']):
    title = metadata.get('source_name', '')
    if title not in title_to_ids:
        title_to_ids[title] = []
    title_to_ids[title].append(all_data['ids'][i])

duplicate_titles = {title: ids for title, ids in title_to_ids.items() if len(ids) > 1}

if duplicate_titles:
    print(f"⚠️  FOUND {len(duplicate_titles)} DUPLICATE TITLES:")
    print("-" * 100)
    for title, ids in list(duplicate_titles.items())[:10]:
        print(f"  Title: {title}")
        print(f"  IDs: {ids[:3]}... ({len(ids)} total)")
        print()
else:
    print("✅ No duplicate titles found")

print()

# Check specific problematic datasets
print("CHECKING SPECIFIC DATASETS:")
print("-" * 100)

problem_titles = [
    "Annual Real Estate Ownership by GCC Citizens by Nationality",
    "Arriving Vessels' Gross and Net Tonnage By Type of Vessel and Country of Registration Doha Port"
]

for title in problem_titles:
    matching_ids = title_to_ids.get(title, [])
    print(f"\nTitle: {title}")
    print(f"Found {len(matching_ids)} instances")
    if len(matching_ids) > 1:
        print(f"IDs: {matching_ids}")
