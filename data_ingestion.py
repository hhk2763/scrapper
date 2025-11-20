"""
Data Ingestion Pipeline for Shipping Intelligence Startup
Processes scraped data and loads it into the database
"""

import pandas as pd
import os
import re
from datetime import datetime
from database_manager import DatabaseManager


class DataIngestionPipeline:
    """Processes and ingests shipping data into the database"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def parse_tonnage(self, value: str) -> float:
        """Parse tonnage values from strings like 'Import(5000.0)' or 'Export(10000.0)'"""
        if pd.isna(value) or value == '':
            return 0.0
        
        match = re.search(r'[\d.]+', str(value))
        if match:
            return float(match.group())
        return 0.0
    
    def ingest_excel_file(self, excel_path: str) -> dict:
        """Ingest data from an Excel file into the database"""
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return {'status': 'error', 'message': 'File not found'}
        
        results = {
            'expected_arrivals': 0,
            'ships_off_port': 0,
            'ship_departures': 0,
            'ships_on_port': 0
        }
        
        try:
            xls = pd.ExcelFile(excel_path)
            
            # Process Expected Arrivals
            if 'Expected Arrivals' in xls.sheet_names:
                results['expected_arrivals'] = self._ingest_expected_arrivals(
                    pd.read_excel(excel_path, sheet_name='Expected Arrivals')
                )
            
            # Process Ships Off Port
            if 'Ships Off Port' in xls.sheet_names:
                results['ships_off_port'] = self._ingest_ships_off_port(
                    pd.read_excel(excel_path, sheet_name='Ships Off Port')
                )
            
            # Process Ship Departures
            if 'Ship Departures' in xls.sheet_names:
                results['ship_departures'] = self._ingest_ship_departures(
                    pd.read_excel(excel_path, sheet_name='Ship Departures')
                )
            
            # Process Ships On Port
            if 'Ship On Port' in xls.sheet_names:
                results['ships_on_port'] = self._ingest_ships_on_port(
                    pd.read_excel(excel_path, sheet_name='Ship On Port')
                )
            
            return {'status': 'success', 'results': results}
            
        except Exception as e:
            print(f"Error ingesting file {excel_path}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _ingest_expected_arrivals(self, df: pd.DataFrame) -> int:
        """Process and ingest expected arrivals data"""
        count = 0
        current_cargo_type = None
        
        for idx, row in df.iterrows():
            # Skip header rows and empty rows
            if pd.isna(row.iloc[0]) or row.iloc[0] == 'Name':
                continue
            
            # Check if this is a cargo type header
            if pd.isna(row.iloc[1]) and not pd.isna(row.iloc[0]):
                current_cargo_type = row.iloc[0]
                continue
            
            # Process data rows
            if not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                try:
                    ship_name = str(row.iloc[0]).strip()
                    shipping_agent = str(row.iloc[1]).strip() if not pd.isna(row.iloc[1]) else ''
                    
                    data = {
                        'ship_name': ship_name,
                        'shipping_agent': shipping_agent,
                        'arrival_date': str(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else None,
                        'import_tons': self.parse_tonnage(row.iloc[3]) if len(row) > 3 else 0.0,
                        'export_tons': self.parse_tonnage(row.iloc[4]) if len(row) > 4 else 0.0,
                        'cargo_type': current_cargo_type
                    }
                    
                    self.db_manager.insert_expected_arrival(data)
                    count += 1
                except Exception as e:
                    print(f"Error processing row {idx}: {e}")
                    continue
        
        return count
    
    def _ingest_ships_off_port(self, df: pd.DataFrame) -> int:
        """Process and ingest ships off port data"""
        count = 0
        
        # Find the header row
        header_row = None
        for idx, row in df.iterrows():
            if 'VesselName' in str(row.iloc[0]) or 'Vessel_name' in str(row.iloc[0]):
                header_row = idx
                break
        
        if header_row is None:
            return 0
        
        # Process data rows after header
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            
            if pd.isna(row.iloc[0]):
                continue
            
            try:
                data = {
                    'ship_name': str(row.iloc[0]).strip(),
                    'vessel_type': str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else None,
                    'flag': str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else None,
                    'rotation': str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else None,
                    'anchorage_date': str(row.iloc[4]).strip() if len(row) > 4 and not pd.isna(row.iloc[4]) else None,
                    'remarks': str(row.iloc[5]).strip() if len(row) > 5 and not pd.isna(row.iloc[5]) else None
                }
                
                self.db_manager.insert_ship_off_port(data)
                count += 1
            except Exception as e:
                print(f"Error processing ships off port row {idx}: {e}")
                continue
        
        return count
    
    def _ingest_ship_departures(self, df: pd.DataFrame) -> int:
        """Process and ingest ship departures data"""
        count = 0
        
        # Find the header row
        header_row = None
        for idx, row in df.iterrows():
            if 'VesselName' in str(row.iloc[0]) or 'Vessel_name' in str(row.iloc[0]):
                header_row = idx
                break
        
        if header_row is None:
            return 0
        
        # Process data rows after header
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            
            if pd.isna(row.iloc[0]):
                continue
            
            try:
                data = {
                    'ship_name': str(row.iloc[0]).strip(),
                    'vessel_type': str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else None,
                    'flag': str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else None,
                    'rotation': str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else None,
                    'departure_date': str(row.iloc[4]).strip() if len(row) > 4 and not pd.isna(row.iloc[4]) else None,
                    'remarks': str(row.iloc[5]).strip() if len(row) > 5 and not pd.isna(row.iloc[5]) else None
                }
                
                self.db_manager.insert_ship_departure(data)
                count += 1
            except Exception as e:
                print(f"Error processing ship departure row {idx}: {e}")
                continue
        
        return count
    
    def _ingest_ships_on_port(self, df: pd.DataFrame) -> int:
        """Process and ingest ships on port data"""
        count = 0
        
        # Find the header row
        header_row = None
        for idx, row in df.iterrows():
            if 'VesselName' in str(row.iloc[0]) or 'Vessel_name' in str(row.iloc[0]):
                header_row = idx
                break
        
        if header_row is None:
            return 0
        
        # Process data rows after header
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            
            if pd.isna(row.iloc[0]):
                continue
            
            try:
                data = {
                    'ship_name': str(row.iloc[0]).strip(),
                    'vessel_type': str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else None,
                    'flag': str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else None,
                    'rotation': str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else None,
                    'berth': str(row.iloc[4]).strip() if len(row) > 4 and not pd.isna(row.iloc[4]) else None,
                    'arrival_date': str(row.iloc[5]).strip() if len(row) > 5 and not pd.isna(row.iloc[5]) else None,
                    'remarks': str(row.iloc[6]).strip() if len(row) > 6 and not pd.isna(row.iloc[6]) else None
                }
                
                self.db_manager.insert_ship_on_port(data)
                count += 1
            except Exception as e:
                print(f"Error processing ships on port row {idx}: {e}")
                continue
        
        return count
    
    def ingest_all_historical_data(self) -> dict:
        """Ingest all historical data from all dated folders"""
        total_results = {
            'expected_arrivals': 0,
            'ships_off_port': 0,
            'ship_departures': 0,
            'ships_on_port': 0,
            'files_processed': 0,
            'files_failed': 0
        }
        
        # Find all dated folders
        folders = sorted([f for f in os.listdir('.') if f.startswith('2025-')])
        
        print(f"Found {len(folders)} dated folders to process")
        
        for folder in folders:
            excel_path = os.path.join(folder, 'expected_arrival.xlsx')
            
            if os.path.exists(excel_path):
                print(f"Processing {excel_path}...")
                result = self.ingest_excel_file(excel_path)
                
                if result['status'] == 'success':
                    for key, value in result['results'].items():
                        total_results[key] += value
                    total_results['files_processed'] += 1
                else:
                    total_results['files_failed'] += 1
        
        return total_results


def main():
    """Main function to run data ingestion"""
    print("Initializing database...")
    db_manager = DatabaseManager()
    
    # Initialize schema
    if os.path.exists('database_schema.sql'):
        db_manager.initialize_schema()
    
    # Create ingestion pipeline
    with db_manager as conn:
        pipeline = DataIngestionPipeline(db_manager)
        
        # Ingest all historical data
        print("\nStarting data ingestion...")
        results = pipeline.ingest_all_historical_data()
        
        print("\n=== Ingestion Results ===")
        print(f"Files processed: {results['files_processed']}")
        print(f"Files failed: {results['files_failed']}")
        print(f"Expected arrivals: {results['expected_arrivals']}")
        print(f"Ships off port: {results['ships_off_port']}")
        print(f"Ship departures: {results['ship_departures']}")
        print(f"Ships on port: {results['ships_on_port']}")
        
        # Show daily statistics
        print("\n=== Daily Statistics ===")
        stats = db_manager.get_daily_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
