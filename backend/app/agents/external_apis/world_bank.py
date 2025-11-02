"""
World Bank API Client
Provides access to GCC economic indicators and international comparisons
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import chromadb

class WorldBankAPI:
    """
    World Bank API client for GCC economic indicators
    """
    
    # Common indicators
    INDICATORS = {
        'gdp': 'NY.GDP.MKTP.CD',  # GDP (current USD)
        'gdp_growth': 'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
        'population': 'SP.POP.TOTL',  # Population, total
        'inflation': 'FP.CPI.TOTL.ZG',  # Inflation, consumer prices (annual %)
        'unemployment': 'SL.UEM.TOTL.ZS',  # Unemployment, total (% of labor force)
        'fdi': 'BX.KLT.DINV.CD.WD',  # Foreign direct investment, net inflows
        'exports': 'NE.EXP.GNFS.CD',  # Exports of goods and services (current USD)
        'imports': 'NE.IMP.GNFS.CD',  # Imports of goods and services (current USD)
        'gdp_per_capita': 'NY.GDP.PCAP.CD',  # GDP per capita (current USD)
    }
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        self.base_url = "https://api.worldbank.org/v2"
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name="world_bank_data")
        except:
            self.collection = self.chroma_client.create_collection(
                name="world_bank_data",
                metadata={"description": "World Bank economic indicators"}
            )
    
    def get_indicator(
        self, 
        countries: List[str],  # ['QA', 'AE', 'SA', 'KW', 'BH', 'OM']
        indicator: str,  # 'NY.GDP.MKTP.CD' (GDP)
        start_year: int = 2020,
        end_year: int = 2024
    ) -> Dict:
        """
        Fetch indicator data from World Bank
        """
        # Build API request - World Bank expects lowercase country codes
        country_codes = ';'.join([c.lower() for c in countries])
        url = f"{self.base_url}/country/{country_codes}/indicator/{indicator}"
        
        params = {
            'format': 'json',
            'date': f'{start_year}:{end_year}',
            'per_page': 1000
        }
        
        headers = {
            'User-Agent': 'UDC-Intelligence-System/1.0 (research@udc.qa)'
        }
        
        print(f"Fetching {indicator} for {countries} ({start_year}-{end_year})...")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                return {'status': 'error', 'error': 'No data returned'}
            
            # Parse results
            results = []
            for item in data[1]:  # Data is in second element
                if item['value'] is not None:  # Skip null values
                    results.append({
                        'country': item['country']['value'],
                        'country_code': item['countryiso3code'],
                        'indicator': item['indicator']['value'],
                        'indicator_code': indicator,
                        'year': item['date'],
                        'value': item['value'],
                        'unit': self._get_indicator_unit(indicator)
                    })
            
            # Cache in ChromaDB
            self._cache_results(indicator, countries, results)
            
            print(f"✓ Retrieved {len(results)} data points")
            
            return {
                'status': 'success',
                'source': 'world_bank_api',
                'indicator': indicator,
                'countries': countries,
                'data': results,
                'retrieved_at': datetime.now().isoformat()
            }
        
        except requests.exceptions.RequestException as e:
            print(f"✗ API Error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _cache_results(self, indicator: str, countries: List[str], data: List[Dict]):
        """Cache API results in ChromaDB"""
        
        if not data:
            return
        
        # Convert to searchable text
        text = f"World Bank Data: {data[0]['indicator']}\n"
        text += f"Indicator Code: {indicator}\n"
        text += f"Countries: {', '.join([d['country'] for d in data if 'country' in d])}\n\n"
        
        for item in data:
            text += f"{item['country']} ({item['year']}): {item['value']:,.2f} {item['unit']}\n"
        
        # Store in ChromaDB
        cache_id = f"wb_{indicator}_{'_'.join(countries)}_{int(datetime.now().timestamp())}"
        
        try:
            self.collection.add(
                documents=[text],
                metadatas=[{
                    'source': 'world_bank_api',
                    'indicator': indicator,
                    'indicator_name': data[0]['indicator'] if data else '',
                    'countries': ','.join(countries),
                    'cached_at': datetime.now().isoformat(),
                    'data_type': 'api_cache',
                    'external_api': 'world_bank'
                }],
                ids=[cache_id]
            )
        except Exception as e:
            print(f"Warning: Could not cache results: {e}")
    
    def _get_indicator_unit(self, indicator: str) -> str:
        """Get unit for indicator"""
        units = {
            'NY.GDP.MKTP.CD': 'USD',
            'NY.GDP.MKTP.KD.ZG': '%',
            'SP.POP.TOTL': 'people',
            'FP.CPI.TOTL.ZG': '%',
            'SL.UEM.TOTL.ZS': '%',
            'BX.KLT.DINV.CD.WD': 'USD',
            'NE.EXP.GNFS.CD': 'USD',
            'NE.IMP.GNFS.CD': 'USD',
            'NY.GDP.PCAP.CD': 'USD'
        }
        return units.get(indicator, 'units')


def query_world_bank(countries: List[str], indicator: str, years: str = "2020:2024"):
    """
    Agent-accessible World Bank query
    
    Examples:
    - query_world_bank(['QA', 'AE', 'SA'], 'gdp', '2020:2024')
    - query_world_bank(['QA'], 'population', '2015:2024')
    """
    client = WorldBankAPI()
    
    # Map friendly names to indicator codes
    indicator_code = client.INDICATORS.get(indicator, indicator)
    
    # Parse years
    start_year, end_year = map(int, years.split(':'))
    
    return client.get_indicator(countries, indicator_code, start_year, end_year)
