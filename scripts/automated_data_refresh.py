#!/usr/bin/env python3
"""
Automated Data Refresh Pipeline
Keep UDC strategic intelligence platform current with automated updates
"""

import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List, Optional

class AutomatedDataRefresh:
    """Automated refresh pipeline for all data sources."""
    
    def __init__(self):
        self.output_dir = Path("qatar_data/global_sources")
        self.refresh_log_dir = Path("qatar_data/refresh_logs")
        self.refresh_log_dir.mkdir(parents=True, exist_ok=True)
        
        self.refresh_results = {
            "refresh_timestamp": datetime.now().isoformat(),
            "sources_refreshed": {},
            "errors": [],
            "next_refresh_due": {}
        }
        
        # Refresh schedules (in days)
        self.refresh_schedules = {
            "world_bank": 30,      # Monthly
            "imf": 90,             # Quarterly
            "weather": 1,          # Daily
            "flight_data": 1,      # Daily
            "currency": 1,         # Daily
            "google_trends": 7,    # Weekly
            "commodity_prices": 30 # Monthly
        }
    
    def refresh_world_bank_data(self):
        """Refresh World Bank economic indicators."""
        print("🏦 Refreshing World Bank Data...")
        
        try:
            wb_dir = self.output_dir / "world_bank"
            
            # GCC countries
            gcc_countries = ["QAT", "SAU", "ARE", "KWT", "BHR", "OMN"]
            
            # Key indicators
            indicators = {
                "NY.GDP.MKTP.CD": "GDP (current US$)",
                "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
                "FP.CPI.TOTL.ZG": "Inflation"
            }
            
            refreshed_datasets = 0
            
            for country in gcc_countries:
                for code, name in indicators.items():
                    try:
                        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{code}"
                        params = {"format": "json", "date": "2020:2024", "per_page": 100}
                        
                        response = requests.get(url, params=params, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if len(data) > 1 and data[1]:
                                # Save refreshed data
                                file_name = f"{country}_{code.replace('.', '_')}_latest.json"
                                file_path = wb_dir / file_name
                                
                                with open(file_path, 'w') as f:
                                    json.dump({
                                        "country": country,
                                        "indicator": code,
                                        "name": name,
                                        "data": data[1],
                                        "refreshed_at": datetime.now().isoformat()
                                    }, f, indent=2)
                                
                                refreshed_datasets += 1
                        
                        time.sleep(0.3)
                    
                    except Exception as e:
                        self.refresh_results["errors"].append(f"World Bank {country} {code}: {str(e)}")
            
            print(f"  ✅ Refreshed {refreshed_datasets} World Bank datasets")
            
            self.refresh_results["sources_refreshed"]["world_bank"] = {
                "status": "success",
                "datasets_refreshed": refreshed_datasets,
                "timestamp": datetime.now().isoformat()
            }
            
            return refreshed_datasets
        
        except Exception as e:
            print(f"  ❌ World Bank refresh error: {e}")
            self.refresh_results["errors"].append(f"World Bank: {str(e)}")
            return 0
    
    def refresh_imf_data(self):
        """Refresh IMF macroeconomic data."""
        print("\n💰 Refreshing IMF Data...")
        
        try:
            imf_dir = self.output_dir / "imf"
            
            # Key IMF indicators
            indicators = ["NGDP_RPCH", "PCPIPCH"]  # GDP growth, Inflation
            
            refreshed = 0
            
            for indicator in indicators:
                try:
                    url = f"https://www.imf.org/external/datamapper/api/v1/{indicator}/QAT"
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        file_path = imf_dir / f"qatar_{indicator}_latest.json"
                        with open(file_path, 'w') as f:
                            json.dump({
                                "indicator": indicator,
                                "data": data,
                                "refreshed_at": datetime.now().isoformat()
                            }, f, indent=2)
                        
                        refreshed += 1
                    
                    time.sleep(0.5)
                
                except Exception as e:
                    self.refresh_results["errors"].append(f"IMF {indicator}: {str(e)}")
            
            print(f"  ✅ Refreshed {refreshed} IMF datasets")
            
            self.refresh_results["sources_refreshed"]["imf"] = {
                "status": "success",
                "datasets_refreshed": refreshed,
                "timestamp": datetime.now().isoformat()
            }
            
            return refreshed
        
        except Exception as e:
            print(f"  ❌ IMF refresh error: {e}")
            self.refresh_results["errors"].append(f"IMF: {str(e)}")
            return 0
    
    def refresh_weather_data(self):
        """Refresh weather forecast for Doha."""
        print("\n☀️ Refreshing Weather Data...")
        
        # Note: Requires OpenWeatherMap API key (free tier available)
        # This is a placeholder - user needs to configure API key
        
        print("  ⚠️ Weather API requires configuration (API key)")
        print("  📋 Sign up at: https://openweathermap.org/api")
        
        self.refresh_results["sources_refreshed"]["weather"] = {
            "status": "requires_api_key",
            "note": "Configure OpenWeatherMap API key for automated refresh"
        }
        
        return 0
    
    def refresh_currency_exchange(self):
        """Refresh currency exchange rates."""
        print("\n💱 Refreshing Currency Exchange Rates...")
        
        try:
            currency_dir = self.output_dir / "currency"
            
            # Using exchangerate-api.com (free tier)
            base_currency = "QAR"
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                file_path = currency_dir / "exchange_rates_latest.json"
                with open(file_path, 'w') as f:
                    json.dump({
                        "base": base_currency,
                        "rates": data.get("rates", {}),
                        "refreshed_at": datetime.now().isoformat(),
                        "date": data.get("date", "")
                    }, f, indent=2)
                
                print(f"  ✅ Refreshed exchange rates for {len(data.get('rates', {}))} currencies")
                
                self.refresh_results["sources_refreshed"]["currency"] = {
                    "status": "success",
                    "currencies_updated": len(data.get("rates", {})),
                    "timestamp": datetime.now().isoformat()
                }
                
                return 1
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        except Exception as e:
            print(f"  ❌ Currency refresh error: {e}")
            self.refresh_results["errors"].append(f"Currency: {str(e)}")
            return 0
    
    def refresh_flight_data(self):
        """Refresh flight arrivals at Hamad International Airport."""
        print("\n✈️ Refreshing Flight Data...")
        
        try:
            flight_dir = self.output_dir / "flight_data"
            
            # OpenSky Network - Hamad International Airport (OTHH)
            airport_icao = "OTHH"
            
            # Get flights in last 24 hours
            end_time = int(time.time())
            start_time = end_time - 86400  # 24 hours ago
            
            url = f"https://opensky-network.org/api/flights/arrival"
            params = {
                "airport": airport_icao,
                "begin": start_time,
                "end": end_time
            }
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                flights = response.json()
                
                file_path = flight_dir / "doha_arrivals_24h.json"
                with open(file_path, 'w') as f:
                    json.dump({
                        "airport": airport_icao,
                        "period": "24_hours",
                        "start_time": start_time,
                        "end_time": end_time,
                        "arrivals_count": len(flights) if flights else 0,
                        "flights": flights if flights else [],
                        "refreshed_at": datetime.now().isoformat()
                    }, f, indent=2)
                
                print(f"  ✅ Refreshed flight data: {len(flights) if flights else 0} arrivals")
                
                self.refresh_results["sources_refreshed"]["flight_data"] = {
                    "status": "success",
                    "arrivals_tracked": len(flights) if flights else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                return 1
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        except Exception as e:
            print(f"  ⚠️ Flight data: {e}")
            self.refresh_results["sources_refreshed"]["flight_data"] = {
                "status": "rate_limited_or_error",
                "note": "OpenSky has rate limits - 10 calls per 10 min"
            }
            return 0
    
    def check_refresh_schedules(self):
        """Check which sources are due for refresh."""
        print("\n📅 Checking Refresh Schedules...")
        
        due_for_refresh = []
        
        for source, days_interval in self.refresh_schedules.items():
            source_dir = self.output_dir / source.replace("_", "")
            
            if source_dir.exists():
                # Find most recent file
                files = list(source_dir.glob("*.json"))
                
                if files:
                    latest_file = max(files, key=lambda f: f.stat().st_mtime)
                    last_modified = datetime.fromtimestamp(latest_file.stat().st_mtime)
                    days_since_update = (datetime.now() - last_modified).days
                    
                    if days_since_update >= days_interval:
                        due_for_refresh.append({
                            "source": source,
                            "days_overdue": days_since_update - days_interval,
                            "last_updated": last_modified.isoformat()
                        })
                        print(f"  ⚠️ {source}: {days_since_update} days since update (refresh every {days_interval} days)")
                    else:
                        next_refresh = last_modified + timedelta(days=days_interval)
                        print(f"  ✅ {source}: Up to date (next refresh: {next_refresh.date()})")
                        self.refresh_results["next_refresh_due"][source] = next_refresh.isoformat()
        
        return due_for_refresh
    
    def generate_refresh_report(self):
        """Generate automated refresh report."""
        print("\n📄 Generating Refresh Report...")
        
        report = {
            "refresh_execution": {
                "timestamp": self.refresh_results["refresh_timestamp"],
                "sources_attempted": list(self.refresh_results["sources_refreshed"].keys()),
                "total_sources": len(self.refresh_results["sources_refreshed"]),
                "errors_count": len(self.refresh_results["errors"])
            },
            "refresh_results": self.refresh_results["sources_refreshed"],
            "errors": self.refresh_results["errors"],
            "next_refresh_schedule": self.refresh_results["next_refresh_due"],
            "refresh_intervals": self.refresh_schedules,
            "status": "completed" if len(self.refresh_results["errors"]) == 0 else "completed_with_errors"
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.refresh_log_dir / f"refresh_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved: {report_file}")
        
        # Also save as latest
        latest_file = self.refresh_log_dir / "latest_refresh_report.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def execute_refresh(self, sources: Optional[List[str]] = None):
        """Execute data refresh for specified sources or all."""
        print("="*80)
        print("AUTOMATED DATA REFRESH PIPELINE")
        print("="*80)
        print()
        
        # Check schedules
        due_sources = self.check_refresh_schedules()
        
        print()
        print("🔄 Executing Data Refresh...")
        print("-" * 80)
        
        # Refresh sources
        if sources is None or "world_bank" in sources:
            self.refresh_world_bank_data()
        
        if sources is None or "imf" in sources:
            self.refresh_imf_data()
        
        if sources is None or "currency" in sources:
            self.refresh_currency_exchange()
        
        if sources is None or "flight_data" in sources:
            self.refresh_flight_data()
        
        if sources is None or "weather" in sources:
            self.refresh_weather_data()
        
        # Generate report
        report = self.generate_refresh_report()
        
        # Summary
        print()
        print("="*80)
        print("REFRESH COMPLETE")
        print("="*80)
        print(f"✅ Sources refreshed: {len(self.refresh_results['sources_refreshed'])}")
        print(f"⚠️ Errors: {len(self.refresh_results['errors'])}")
        
        if self.refresh_results['errors']:
            print("\nErrors encountered:")
            for error in self.refresh_results['errors'][:5]:
                print(f"  - {error}")
        
        print(f"\n📊 Detailed report: {self.refresh_log_dir / 'latest_refresh_report.json'}")
        
        return report


def main():
    """Execute automated refresh."""
    print("UDC Automated Data Refresh Pipeline")
    print("="*50)
    
    refresher = AutomatedDataRefresh()
    
    # Execute refresh for free API sources
    refresher.execute_refresh(sources=["world_bank", "imf", "currency", "flight_data"])


if __name__ == "__main__":
    main()
