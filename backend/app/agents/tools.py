"""
Tools available to agents for data retrieval and analysis.

Tools are functions that agents can call to access UDC data, perform calculations,
or interact with external systems.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings


class UDCDataTools:
    """
    Collection of tools for accessing UDC data.
    
    These tools provide agents with access to financial data, property metrics,
    and other UDC-specific information.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize UDC data tools.
        
        Args:
            data_dir: Path to sample data directory. Defaults to settings value.
        """
        if data_dir is None:
            # Use absolute path to data/sample_data from project root
            # Get the project root (4 levels up from this file: tools.py -> agents -> app -> backend -> root)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            self.data_dir = project_root / "data" / "sample_data"
        else:
            self.data_dir = Path(data_dir)
    
    def _load_json_data(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON data file.
        
        Args:
            filename: Name of JSON file to load.
            
        Returns:
            dict: Parsed JSON data.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file is not valid JSON.
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_financial_summary(self, period: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve UDC financial summary data.
        
        Args:
            period: Specific period (e.g., "2023", "2024_9m", "Q3 2024").
                   If None, returns all available data.
        
        Returns:
            dict: Financial summary data including revenue, profit, debt, etc.
            
        Example:
            >>> tools = UDCDataTools()
            >>> data = tools.get_financial_summary("2023")
            >>> print(f"Revenue: QAR {data['revenue']:,}K")
        """
        data = self._load_json_data("financial_summary.json")
        
        if period is None:
            return data
        
        # Search for matching period in annual summary
        for annual in data.get("annual_summary", []):
            if str(annual.get("year")) == str(period) or annual.get("period") == period:
                return {
                    "period": period,
                    "data": annual,
                    "metadata": data.get("metadata", {})
                }
        
        # Search quarterly data
        for quarterly in data.get("quarterly_performance", []):
            if quarterly.get("period") == period:
                return {
                    "period": period,
                    "data": quarterly,
                    "metadata": data.get("metadata", {})
                }
        
        return {"error": f"No data found for period: {period}", "available_periods": [
            item.get("year") or item.get("period") 
            for item in data.get("annual_summary", []) + data.get("quarterly_performance", [])
        ]}
    
    def get_debt_metrics(self) -> Dict[str, Any]:
        """
        Retrieve current debt and leverage metrics.
        
        Returns:
            dict: Debt metrics including debt-to-equity, coverage ratios, etc.
        """
        data = self._load_json_data("financial_summary.json")
        
        # Get most recent data (2024 9M)
        latest = data["annual_summary"][1]  # 2024 data
        
        return {
            "total_debt_qar": latest["total_debt"],
            "total_equity_qar": latest["total_equity"],
            "debt_to_equity": latest["debt_to_equity"],
            "cash_and_equivalents_qar": latest["cash_and_equivalents"],
            "thresholds": data["key_metrics_thresholds"],
            "credit_facilities": data.get("credit_facilities", {}),
            "status": "YELLOW FLAG" if latest["debt_to_equity"] >= 0.48 else "GREEN",
            "commentary": "Approaching yellow flag threshold of 0.50 due to Gewan capex"
        }
    
    def get_property_metrics(self, property_name: str = "pearl") -> Dict[str, Any]:
        """
        Retrieve property portfolio metrics.
        
        Args:
            property_name: Property to query ("pearl", "gewan", "all").
            
        Returns:
            dict: Property metrics including occupancy, pricing, etc.
        """
        data = self._load_json_data("property_portfolio.json")
        
        if property_name.lower() == "pearl":
            return {
                "property": "The Pearl-Qatar",
                "data": data["the_pearl_qatar"],
                "metadata": data["metadata"]
            }
        elif property_name.lower() == "gewan":
            return {
                "property": "Gewan Island",
                "data": data["gewan_island"],
                "metadata": data["metadata"]
            }
        else:
            return data
    
    def get_qatar_cool_metrics(self) -> Dict[str, Any]:
        """
        Retrieve Qatar Cool operational and financial metrics.
        
        Returns:
            dict: Qatar Cool performance data.
        """
        return self._load_json_data("qatar_cool_metrics.json")
    
    def get_market_indicators(self) -> Dict[str, Any]:
        """
        Retrieve Qatar real estate market indicators.
        
        Returns:
            dict: Market data including competitors, trends, demographics.
        """
        return self._load_json_data("market_indicators.json")
    
    def get_subsidiaries_performance(self) -> Dict[str, Any]:
        """
        Retrieve subsidiary company performance (HDC, USI, etc.).
        
        Returns:
            dict: Subsidiary financial and operational data.
        """
        return self._load_json_data("subsidiaries_performance.json")
    
    def search_data(self, query: str) -> Dict[str, Any]:
        """
        Search across all UDC data for relevant information.
        
        Args:
            query: Natural language search query.
            
        Returns:
            dict: Relevant data matching the query.
            
        Note:
            This is a simple keyword-based search for MVP.
            Phase 2 will use vector embeddings and semantic search.
        """
        results = []
        query_lower = query.lower()
        
        # Search keywords mapping
        keywords_map = {
            "debt": ["debt", "leverage", "borrowing", "loan"],
            "revenue": ["revenue", "income", "sales", "earnings"],
            "profit": ["profit", "earnings", "ebitda", "margin"],
            "pearl": ["pearl", "island", "residential", "occupancy"],
            "gewan": ["gewan", "crystal", "phase"],
            "qatar cool": ["qatar cool", "cooling", "district", "energy"],
            "hdc": ["hdc", "hotel", "hospitality", "marina"],
        }
        
        # Determine what data to retrieve
        for category, keywords in keywords_map.items():
            if any(keyword in query_lower for keyword in keywords):
                try:
                    if "debt" in category:
                        results.append({"category": "debt", "data": self.get_debt_metrics()})
                    elif "pearl" in category:
                        results.append({"category": "pearl", "data": self.get_property_metrics("pearl")})
                    elif "gewan" in category:
                        results.append({"category": "gewan", "data": self.get_property_metrics("gewan")})
                    elif "qatar cool" in category:
                        results.append({"category": "qatar_cool", "data": self.get_qatar_cool_metrics()})
                    elif "hdc" in category:
                        results.append({"category": "subsidiaries", "data": self.get_subsidiaries_performance()})
                except Exception as e:
                    results.append({"category": category, "error": str(e)})
        
        # If no specific category matched, return general financial summary
        if not results:
            results.append({
                "category": "financial_summary",
                "data": self.get_financial_summary()
            })
        
        return {
            "query": query,
            "results_found": len(results),
            "results": results
        }


# Create singleton instance for easy import
udc_tools = UDCDataTools()

