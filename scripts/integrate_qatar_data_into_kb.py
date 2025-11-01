#!/usr/bin/env python3
"""
Integrate Qatar Government Data into UDC Knowledge Base
Processes downloaded Qatar datasets and adds them to the semantic search system

Author: AI Development Team
Date: October 31, 2025
Purpose: Transform raw Qatar government data into agent-accessible intelligence
"""

import pandas as pd
import json
from pathlib import Path
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path for knowledge base access
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

class QatarDataIntegrator:
    """Integrate Qatar government datasets into UDC knowledge base."""
    
    def __init__(self):
        self.qatar_data_dir = Path("qatar_data/critical_priority")
        self.processed_data = []
        
        # Strategic context mapping for each dataset
        self.dataset_contexts = {
            "hotels-and-restaurants-statistics": {
                "udc_relevance": "Direct hospitality performance benchmarking for UDC hotel investments",
                "agent_use": "Dr. Noor (Market Intelligence), Dr. James (Financial Analysis)",
                "strategic_impact": "Hospitality revenue trends, competitive positioning, market demand"
            },
            "main-economic-indicators": {
                "udc_relevance": "Multi-sector economic indicators for strategic investment timing",
                "agent_use": "Dr. Omar (Orchestrator), Dr. James (CFO), Dr. Noor (Market)",
                "strategic_impact": "GDP growth, sector performance, investment timing signals"
            },
            "quarterly-gdp": {
                "udc_relevance": "Economic growth by sector for billion-riyal investment decisions",
                "agent_use": "Dr. James (Financial Analysis), Dr. Omar (Strategic Timing)",
                "strategic_impact": "Sector-specific growth rates, economic momentum indicators"
            },
            "water-consumption": {
                "udc_relevance": "Utility demand patterns for Qatar Cool district cooling operations",
                "agent_use": "Qatar Cool subsidiary analysis, infrastructure planning",
                "strategic_impact": "Cooling demand forecasting, utility infrastructure capacity"
            },
            "water-storage": {
                "udc_relevance": "Water infrastructure capacity for large development projects",
                "agent_use": "Development feasibility analysis, infrastructure planning",
                "strategic_impact": "Infrastructure constraints, development timing, capacity planning"
            },
            "households": {
                "udc_relevance": "Household formation trends for residential demand forecasting",
                "agent_use": "Dr. Noor (Market Intelligence), residential development planning",
                "strategic_impact": "Population growth, household size trends, residential demand"
            },
            "employees": {
                "udc_relevance": "Employment by sector for commercial leasing intelligence",
                "agent_use": "Dr. Noor (Market Intelligence), commercial leasing strategy",
                "strategic_impact": "Employment growth, sector employment, commercial tenant demand"
            }
        }
    
    def process_all_qatar_datasets(self):
        """Process all downloaded Qatar datasets for knowledge base integration."""
        
        print("="*80)
        print("UDC POLARIS - INTEGRATING QATAR GOVERNMENT DATA")
        print("="*80)
        print("Converting raw government data into agent-accessible intelligence")
        
        if not self.qatar_data_dir.exists():
            print(f"❌ Error: {self.qatar_data_dir} does not exist")
            print("Run download_verified_priority_datasets.py first")
            return []
        
        csv_files = list(self.qatar_data_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"❌ No CSV files found in {self.qatar_data_dir}")
            return []
        
        print(f"Found {len(csv_files)} Qatar government datasets")
        
        processed_documents = []
        
        for i, csv_file in enumerate(csv_files, 1):
            print(f"\n[{i:2d}/{len(csv_files)}] Processing {csv_file.name}")
            
            doc = self._process_single_dataset(csv_file)
            if doc:
                processed_documents.append(doc)
                print(f"    ✅ Processed: {len(doc.get('summary', '').split())} words")
            else:
                print(f"    ❌ Failed to process")
        
        print(f"\n📊 INTEGRATION SUMMARY")
        print(f"{'='*50}")
        print(f"✅ Processed: {len(processed_documents)}/{len(csv_files)} datasets")
        print(f"📝 Total content: {sum(len(doc.get('summary', '').split()) for doc in processed_documents)} words")
        print(f"🎯 Strategic categories: Economy, Demographics, Hospitality, Utilities, Labor")
        
        # Save processed data summary
        self._save_integration_report(processed_documents)
        
        return processed_documents
    
    def _process_single_dataset(self, csv_file: Path) -> Dict[str, Any]:
        """Process a single Qatar government dataset."""
        
        try:
            # Load the CSV data - Qatar uses semicolon delimiters
            df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', on_bad_lines='skip')
            
            # Load metadata if available
            metadata_file = csv_file.parent / f"{csv_file.stem}_metadata.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            # Identify dataset type and context
            dataset_name = csv_file.stem
            context = self._identify_dataset_context(dataset_name)
            
            # Generate intelligent summary
            summary = self._generate_dataset_summary(df, dataset_name, metadata, context)
            
            # Create document for knowledge base
            document = {
                "source": f"Qatar Open Data Portal - {dataset_name}",
                "type": "government_data",
                "category": "qatar_statistics",
                "dataset_name": dataset_name,
                "summary": summary,
                "metadata": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "downloaded_at": metadata.get("downloaded_at"),
                    "priority": metadata.get("priority", 0),
                    "business_impact": metadata.get("business_impact", ""),
                    "udc_relevance": context.get("udc_relevance", ""),
                    "strategic_agents": context.get("agent_use", ""),
                    "strategic_impact": context.get("strategic_impact", "")
                },
                "columns": df.columns.tolist(),
                "sample_data": df.head(3).to_dict('records') if len(df) > 0 else []
            }
            
            return document
            
        except Exception as e:
            print(f"    Error processing {csv_file}: {str(e)}")
            return {}
    
    def _identify_dataset_context(self, dataset_name: str) -> Dict[str, str]:
        """Identify the strategic context for a dataset."""
        
        dataset_lower = dataset_name.lower()
        
        for key, context in self.dataset_contexts.items():
            if key in dataset_lower:
                return context
        
        # Default context for unmatched datasets
        return {
            "udc_relevance": "Qatar government statistical data relevant to market intelligence",
            "agent_use": "General market intelligence and strategic context",
            "strategic_impact": "Market context and government statistical reference"
        }
    
    def _generate_dataset_summary(self, df: pd.DataFrame, dataset_name: str, metadata: dict, context: dict) -> str:
        """Generate an intelligent summary of the dataset for the knowledge base."""
        
        summary_parts = [
            f"QATAR GOVERNMENT DATA: {dataset_name.replace('-', ' ').title()}",
            f"\nSOURCE: Qatar Open Data Portal (Official Government Statistics)",
            f"STRATEGIC RELEVANCE: {context.get('udc_relevance', 'Market intelligence data')}",
            f"TARGET AGENTS: {context.get('agent_use', 'General intelligence')}",
            f"\nDATASET OVERVIEW:"
        ]
        
        # Add data structure info
        if not df.empty:
            summary_parts.extend([
                f"• Contains {len(df)} records across {len(df.columns)} data fields",
                f"• Data columns: {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}",
                f"• Most recent data available from Qatar Planning & Statistics Authority"
            ])
            
            # Add sample insights based on dataset type
            if "economic" in dataset_name.lower() or "gdp" in dataset_name.lower():
                summary_parts.extend([
                    f"\nECONOMIC INTELLIGENCE:",
                    f"• Sector-wise economic performance data for strategic investment timing",
                    f"• GDP growth indicators for billion-riyal investment decisions",
                    f"• Economic activity trends across Qatar's major industries"
                ])
            
            elif "hotel" in dataset_name.lower() or "restaurant" in dataset_name.lower():
                summary_parts.extend([
                    f"\nHOSPITALITY INTELLIGENCE:",
                    f"• Hotel and restaurant sector performance metrics",
                    f"• Revenue trends for UDC hospitality investment benchmarking",
                    f"• Market demand indicators for tourism and business travel"
                ])
            
            elif "water" in dataset_name.lower():
                summary_parts.extend([
                    f"\nUTILITY & INFRASTRUCTURE INTELLIGENCE:",
                    f"• Water consumption and storage capacity data",
                    f"• Critical for Qatar Cool district cooling demand forecasting",
                    f"• Infrastructure capacity planning for large developments"
                ])
            
            elif "household" in dataset_name.lower() or "population" in dataset_name.lower():
                summary_parts.extend([
                    f"\nDEMOGRAPHIC INTELLIGENCE:",
                    f"• Population and household formation trends",
                    f"• Residential demand forecasting for Pearl-Qatar and Gewan Island",
                    f"• Target market sizing for luxury and family residential products"
                ])
            
            elif "employee" in dataset_name.lower() or "labor" in dataset_name.lower():
                summary_parts.extend([
                    f"\nLABOR MARKET INTELLIGENCE:",
                    f"• Employment trends by sector and nationality",
                    f"• Commercial leasing demand indicators",
                    f"• Workforce demographics for office space planning"
                ])
            
            # Add strategic impact
            summary_parts.extend([
                f"\nSTRATEGIC IMPACT FOR UDC:",
                f"• {context.get('strategic_impact', 'Market intelligence and strategic context')}",
                f"• Enables data-driven decisions for billion-riyal investments",
                f"• Provides government-validated statistics for board presentations"
            ])
            
            # Add sample data insights
            if len(df) > 0:
                try:
                    # Try to extract meaningful sample insights
                    sample_insights = self._extract_sample_insights(df, dataset_name)
                    if sample_insights:
                        summary_parts.extend([
                            f"\nSAMPLE DATA INSIGHTS:",
                            *sample_insights
                        ])
                except:
                    pass  # Skip if sample analysis fails
        
        summary_parts.extend([
            f"\nDATA ACCESS: Available through UDC Polaris agent system",
            f"LAST UPDATED: {metadata.get('downloaded_at', 'Unknown')}",
            f"CITATION: Qatar Open Data Portal, accessed {datetime.now().strftime('%B %d, %Y')}"
        ])
        
        return "\n".join(summary_parts)
    
    def _extract_sample_insights(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """Extract sample insights from the actual data."""
        
        insights = []
        
        try:
            # Numerical column insights
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols[:2]:  # First 2 numeric columns
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        mean_val = df[col].mean()
                        max_val = df[col].max()
                        insights.append(f"• {col}: Average {mean_val:.1f}, Maximum {max_val:.1f}")
            
            # Categorical insights
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                for col in categorical_cols[:2]:
                    unique_count = df[col].nunique()
                    most_common = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A"
                    insights.append(f"• {col}: {unique_count} categories, most common: {most_common}")
            
        except:
            pass  # Skip insights if analysis fails
        
        return insights[:3]  # Limit to 3 insights
    
    def _save_integration_report(self, processed_documents: List[Dict[str, Any]]):
        """Save integration report for tracking."""
        
        report = {
            "integration_date": datetime.now().isoformat(),
            "total_datasets": len(processed_documents),
            "datasets_summary": []
        }
        
        for doc in processed_documents:
            report["datasets_summary"].append({
                "dataset_name": doc["dataset_name"],
                "rows": doc["metadata"]["rows"],
                "columns": doc["metadata"]["columns"],
                "priority": doc["metadata"]["priority"],
                "strategic_impact": doc["metadata"]["strategic_impact"]
            })
        
        report_path = self.qatar_data_dir / "integration_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Integration report saved: {report_path}")


def main():
    """Execute Qatar data integration."""
    
    print("UDC Polaris - Qatar Government Data Integration")
    print("=" * 50)
    print("Transform raw Qatar data into agent intelligence")
    
    integrator = QatarDataIntegrator()
    processed_docs = integrator.process_all_qatar_datasets()
    
    if processed_docs:
        print(f"\n🎉 SUCCESS! Processed {len(processed_docs)} Qatar government datasets")
        print("\n🎯 STRATEGIC INTELLIGENCE NOW AVAILABLE:")
        
        categories = {}
        for doc in processed_docs:
            impact = doc["metadata"]["strategic_impact"]
            if "Economic" in impact or "GDP" in impact:
                categories["Economy"] = categories.get("Economy", 0) + 1
            elif "Hospitality" in impact or "hotel" in impact.lower():
                categories["Hospitality"] = categories.get("Hospitality", 0) + 1
            elif "Demographic" in impact or "household" in impact.lower():
                categories["Demographics"] = categories.get("Demographics", 0) + 1
            elif "Utility" in impact or "water" in impact.lower():
                categories["Utilities"] = categories.get("Utilities", 0) + 1
            else:
                categories["Other"] = categories.get("Other", 0) + 1
        
        for category, count in categories.items():
            print(f"  • {category}: {count} datasets")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Add processed data to knowledge base semantic search")
        print(f"2. Update agent prompts to reference Qatar government data")
        print(f"3. Test Dr. James and Dr. Noor with real Qatar statistics")
        print(f"4. Create executive dashboard with government data indicators")
        
    else:
        print("\n❌ No data processed - check downloaded datasets")


if __name__ == "__main__":
    main()
