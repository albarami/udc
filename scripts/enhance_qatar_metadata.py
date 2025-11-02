"""
Metadata Enhancement for Qatar Datasets
Add domain, searchable keywords, and business relevance metadata
"""

import sys
sys.path.insert(0, 'D:/udc')

import chromadb
from typing import Dict, List, Set
import re

class MetadataEnhancer:
    """Enhance metadata for all Qatar datasets"""
    
    # Domain categorization
    DOMAIN_KEYWORDS = {
        'tourism': ['hotel', 'tourism', 'hospitality', 'accommodation', 'guest', 'visitor', 'tourist'],
        'economy': ['gdp', 'economic', 'economy', 'growth', 'value added', 'national accounts', 'macro'],
        'employment': ['employment', 'labor', 'workforce', 'job', 'worker', 'employee', 'wage', 'salary', 'compensation'],
        'demographics': ['population', 'demographic', 'census', 'inhabitants', 'residents', 'household'],
        'real_estate': ['real estate', 'property', 'housing', 'construction', 'building', 'ownership'],
        'infrastructure': ['water', 'electricity', 'utilities', 'energy', 'power', 'production', 'consumption'],
        'transportation': ['vehicle', 'driving', 'license', 'transport', 'traffic', 'airport', 'port'],
        'health': ['health', 'hospital', 'clinic', 'medical', 'patient', 'disease'],
        'education': ['education', 'school', 'student', 'teacher', 'university', 'training'],
        'trade': ['import', 'export', 'trade', 'certificate', 'origin', 'business'],
        'sports': ['sport', 'athlete', 'championship', 'federation', 'club'],
        'environment': ['environment', 'pollution', 'air quality', 'waste', 'emission'],
        'government': ['government', 'ministry', 'public', 'park', 'service'],
        'finance': ['bank', 'insurance', 'financial', 'investment'],
        'agriculture': ['agriculture', 'fishing', 'farm', 'crop'],
        'judicial': ['court', 'judge', 'lawyer', 'legal', 'lawsuit'],
        'maritime': ['vessel', 'port', 'ship', 'cargo', 'tonnage']
    }
    
    # CEO question mapping
    CEO_QUESTIONS = {
        'hotel_performance': ['hotel', 'occupancy', 'adr', 'revpar', 'guest', 'tourism'],
        'real_estate_market': ['real estate', 'property', 'housing', 'construction', 'building'],
        'economic_growth': ['gdp', 'economic', 'growth', 'value added'],
        'labor_market': ['employment', 'wage', 'salary', 'workforce', 'labor'],
        'demographics': ['population', 'census', 'demographic', 'household'],
        'infrastructure_costs': ['water', 'electricity', 'utilities', 'consumption'],
        'market_indicators': ['trade', 'import', 'export', 'business'],
        'quality_of_life': ['health', 'education', 'sports', 'environment']
    }
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        """Initialize enhancer"""
        print(f"Initializing Metadata Enhancer")
        print(f"ChromaDB path: {chroma_path}")
        
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Check if collection exists
        try:
            self.collection = self.chroma_client.get_collection("udc_intelligence")
            print(f"✓ Found collection: udc_intelligence")
        except:
            print("✗ Collection 'udc_intelligence' not found!")
            print("  Creating new collection...")
            self.collection = self.chroma_client.create_collection("udc_intelligence")
        
        print()
    
    def categorize_filename(self, filename: str) -> str:
        """Determine domain from filename"""
        filename_lower = filename.lower()
        
        # Count matches per domain
        domain_scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in filename_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            # Return domain with highest score
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return 'other'
    
    def extract_searchable_keywords(self, filename: str) -> List[str]:
        """Extract meaningful keywords from filename"""
        # Remove .csv extension
        filename = filename.replace('.csv', '')
        
        # Split on hyphens and underscores
        words = re.split(r'[-_]', filename)
        
        # Filter out common words and single letters
        stop_words = {'by', 'and', 'of', 'in', 'the', 'a', 'an', 'to', 'for', 'at', 'on'}
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 1]
        
        # Return unique keywords
        return list(set(keywords))
    
    def map_to_ceo_questions(self, filename: str, domain: str) -> List[str]:
        """Map dataset to relevant CEO question types"""
        filename_lower = filename.lower()
        relevant_questions = []
        
        for question, keywords in self.CEO_QUESTIONS.items():
            if any(kw in filename_lower for kw in keywords):
                relevant_questions.append(question)
        
        # Also add domain-based question
        if domain == 'tourism':
            if 'hotel_performance' not in relevant_questions:
                relevant_questions.append('hotel_performance')
        elif domain == 'real_estate':
            if 'real_estate_market' not in relevant_questions:
                relevant_questions.append('real_estate_market')
        elif domain == 'economy':
            if 'economic_growth' not in relevant_questions:
                relevant_questions.append('economic_growth')
        elif domain == 'employment':
            if 'labor_market' not in relevant_questions:
                relevant_questions.append('labor_market')
        
        return relevant_questions if relevant_questions else ['general_inquiry']
    
    def enhance_all_metadata(self):
        """Enhance metadata for all documents in collection"""
        print(f"{'='*80}")
        print("ENHANCING METADATA FOR ALL QATAR DATASETS")
        print(f"{'='*80}\n")
        
        # Get all documents
        try:
            all_docs = self.collection.get()
        except Exception as e:
            print(f"✗ Error getting documents: {e}")
            return
        
        if not all_docs or not all_docs['ids']:
            print("✗ No documents found in collection!")
            return
        
        total_docs = len(all_docs['ids'])
        print(f"Found {total_docs} documents to enhance\n")
        
        enhanced_count = 0
        skipped_count = 0
        
        for i, (doc_id, metadata) in enumerate(zip(all_docs['ids'], all_docs['metadatas']), 1):
            # Skip if not Qatar CSV
            if 'source' not in metadata:
                skipped_count += 1
                continue
            
            filename = metadata['source']
            
            # Skip if already enhanced
            if 'domain' in metadata and 'business_relevance' in metadata:
                skipped_count += 1
                if i % 100 == 0:
                    print(f"  [{i}/{total_docs}] Already enhanced: {filename[:60]}...")
                continue
            
            # Determine domain
            domain = self.categorize_filename(filename)
            
            # Extract searchable keywords
            keywords = self.extract_searchable_keywords(filename)
            
            # Map to CEO questions
            ceo_relevance = self.map_to_ceo_questions(filename, domain)
            
            # Create enhanced metadata
            enhanced_metadata = {
                **metadata,
                'domain': domain,
                'searchable_keywords': ','.join(keywords[:10]),  # Store as comma-separated
                'business_relevance': ','.join(ceo_relevance),
                'enhanced_date': '2025-11-02'
            }
            
            # Update in ChromaDB
            try:
                self.collection.update(
                    ids=[doc_id],
                    metadatas=[enhanced_metadata]
                )
                enhanced_count += 1
                
                if i % 50 == 0 or i == total_docs:
                    print(f"  [{i}/{total_docs}] Enhanced: {filename[:50]}... → domain: {domain}")
            
            except Exception as e:
                print(f"  ✗ Error updating {doc_id}: {e}")
        
        # Summary
        print(f"\n{'='*80}")
        print("METADATA ENHANCEMENT COMPLETE")
        print(f"{'='*80}")
        print(f"Total documents: {total_docs}")
        print(f"Enhanced: {enhanced_count}")
        print(f"Skipped (already enhanced): {skipped_count}")
        print(f"{'='*80}\n")
        
        return {
            'total': total_docs,
            'enhanced': enhanced_count,
            'skipped': skipped_count
        }
    
    def verify_enhancement(self, sample_size: int = 10):
        """Verify enhanced metadata"""
        print(f"\n{'='*80}")
        print(f"VERIFICATION: Checking {sample_size} sample documents")
        print(f"{'='*80}\n")
        
        # Get sample
        all_docs = self.collection.get(limit=sample_size)
        
        for metadata in all_docs['metadatas']:
            filename = metadata.get('source', 'unknown')
            domain = metadata.get('domain', 'NOT SET')
            keywords = metadata.get('searchable_keywords', 'NOT SET')
            relevance = metadata.get('business_relevance', 'NOT SET')
            
            print(f"File: {filename[:60]}")
            print(f"  Domain: {domain}")
            print(f"  Keywords: {keywords[:100]}")
            print(f"  Business: {relevance}")
            print()
        
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    
    enhancer = MetadataEnhancer()
    
    # Enhance all metadata
    stats = enhancer.enhance_all_metadata()
    
    # Verify enhancement
    enhancer.verify_enhancement(sample_size=10)
    
    return stats


if __name__ == "__main__":
    stats = main()
