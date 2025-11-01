"""
Excel Data Processing

Extracts and structures data from Excel files including:
- Financial models
- KPI trackers
- Analyst data
- Performance metrics

All sheets are parsed and made queryable.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class ExcelProcessor:
    """
    Process Excel files into queryable structured format.
    
    Features:
    - Multi-sheet extraction
    - Column type detection
    - Summary statistics
    - Data validation
    - Missing value handling
    """
    
    def __init__(self, data_dir: str = "D:/udc/data"):
        """Initialize Excel processor with data directory."""
        self.data_dir = Path(data_dir)
        self.processed_count = 0
        self.error_count = 0
    
    def process_all_excel(self) -> List[Dict[str, Any]]:
        """
        Process all Excel files in the data directory.
        
        Returns:
            List of processed Excel file dictionaries with all sheets
        """
        
        excel_files = list(self.data_dir.rglob("*.xlsx")) + list(self.data_dir.rglob("*.xls"))
        print(f"\n{'='*80}")
        print(f"PROCESSING {len(excel_files)} EXCEL FILES")
        print(f"{'='*80}\n")
        
        all_data = []
        start_time = datetime.now()
        
        for idx, excel_file in enumerate(excel_files, 1):
            print(f"[{idx}/{len(excel_files)}] Processing: {excel_file.name}")
            excel_data = self._process_single_excel(excel_file)
            
            if excel_data:
                all_data.append(excel_data)
                self.processed_count += 1
                print(f"      [OK] Extracted {excel_data['sheet_count']} sheets")
            else:
                self.error_count += 1
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print(f"EXCEL PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"  Success: {self.processed_count} files")
        print(f"  Errors: {self.error_count} files")
        print(f"  Total sheets: {sum(e['sheet_count'] for e in all_data)}")
        print(f"  Processing time: {elapsed:.1f} seconds")
        print(f"{'='*80}\n")
        
        return all_data
    
    def _process_single_excel(self, excel_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single Excel file with all sheets.
        
        Args:
            excel_path: Path to Excel file
            
        Returns:
            Dictionary containing Excel data or None if error
        """
        
        try:
            # Read all sheets
            sheets_dict = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl' if excel_path.suffix == '.xlsx' else 'xlrd')
            
            excel_data = {
                'source': excel_path.name,
                'type': 'excel',
                'path': str(excel_path),
                'sheets': {},
                'sheet_count': len(sheets_dict),
                'processed_at': datetime.now().isoformat()
            }
            
            for sheet_name, df in sheets_dict.items():
                # Clean sheet name
                clean_sheet_name = str(sheet_name).strip()
                
                # Handle empty sheets
                if df.empty:
                    print(f"        [WARN] Sheet '{clean_sheet_name}' is empty, skipping")
                    continue
                
                # Convert to records, handle NaN
                records = df.fillna('').to_dict('records')
                
                # Generate summary
                summary = self._generate_summary(df)
                
                excel_data['sheets'][clean_sheet_name] = {
                    'data': records,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'column_count': len(df.columns),
                    'summary': summary
                }
                
                print(f"        Sheet '{clean_sheet_name}': {len(df)} rows × {len(df.columns)} columns")
            
            return excel_data if excel_data['sheets'] else None
            
        except Exception as e:
            print(f"        [ERROR] {str(e)[:100]}")
            return None
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for a sheet.
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Summary statistics dictionary
        """
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'numeric_columns': numeric_cols,
            'text_columns': text_cols,
            'date_columns': date_cols,
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # Add numeric statistics if available
        if numeric_cols:
            stats = df[numeric_cols].describe().to_dict()
            summary['statistics'] = stats
        
        # Add missing value info
        missing = df.isnull().sum()
        if missing.sum() > 0:
            summary['missing_values'] = missing[missing > 0].to_dict()
        
        return summary
    
    def get_processing_summary(self, excel_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of processed Excel files.
        
        Args:
            excel_data: List of processed Excel file dictionaries
            
        Returns:
            Summary dictionary
        """
        
        total_sheets = sum(e['sheet_count'] for e in excel_data)
        total_rows = sum(
            sum(sheet['rows'] for sheet in e['sheets'].values())
            for e in excel_data
        )
        
        return {
            'total_files': len(excel_data),
            'total_sheets': total_sheets,
            'total_rows': total_rows,
            'files': [e['source'] for e in excel_data],
            'processed_at': datetime.now().isoformat()
        }


# Test function
def test_excel_processor():
    """Test Excel processor with actual UDC data."""
    print("Testing Excel Processor...")
    
    processor = ExcelProcessor()
    excel_data = processor.process_all_excel()
    
    if excel_data:
        summary = processor.get_processing_summary(excel_data)
        
        print("\n" + "="*80)
        print("PROCESSING SUMMARY")
        print("="*80)
        print(f"Total Files: {summary['total_files']}")
        print(f"Total Sheets: {summary['total_sheets']}")
        print(f"Total Rows: {summary['total_rows']}")
        print(f"\nFiles Processed:")
        for file in summary['files']:
            print(f"  - {file}")
        
        # Show sample from first file
        if excel_data:
            first_file = excel_data[0]
            print(f"\nSample from '{first_file['source']}':")
            for sheet_name, sheet_data in first_file['sheets'].items():
                print(f"  Sheet '{sheet_name}': {sheet_data['rows']} rows, {sheet_data['column_count']} columns")
                print(f"    Columns: {', '.join(sheet_data['columns'][:5])}" + ("..." if len(sheet_data['columns']) > 5 else ""))


if __name__ == "__main__":
    test_excel_processor()

