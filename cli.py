#!/usr/bin/env python3
"""
CLI Tool for Shipping Intelligence Database Management
"""

import argparse
import sys
from database_manager import DatabaseManager
from data_ingestion import DataIngestionPipeline
from analytics import ShippingAnalytics


def init_database(args):
    """Initialize database with schema"""
    db = DatabaseManager(args.db_path)
    db.initialize_schema()
    print(f"✓ Database initialized: {args.db_path}")


def import_data(args):
    """Import data from Excel files"""
    db = DatabaseManager(args.db_path)
    pipeline = DataIngestionPipeline(db)
    
    with db as conn:
        if args.file:
            print(f"Importing from {args.file}...")
            result = pipeline.ingest_excel_file(args.file)
            if result['status'] == 'success':
                print("✓ Import successful:")
                for key, value in result['results'].items():
                    print(f"  - {key}: {value} records")
            else:
                print(f"✗ Import failed: {result.get('message', 'Unknown error')}")
        else:
            print("Importing all historical data...")
            result = pipeline.ingest_all_historical_data()
            print("✓ Import complete:")
            print(f"  - Files processed: {result['files_processed']}")
            print(f"  - Files failed: {result['files_failed']}")
            print(f"  - Expected arrivals: {result['expected_arrivals']}")
            print(f"  - Ships off port: {result['ships_off_port']}")
            print(f"  - Ship departures: {result['ship_departures']}")
            print(f"  - Ships on port: {result['ships_on_port']}")


def show_stats(args):
    """Show database statistics"""
    db = DatabaseManager(args.db_path)
    
    with db as conn:
        cursor = conn.cursor()
        
        print("\n=== Database Statistics ===\n")
        
        # Ship count
        cursor.execute("SELECT COUNT(*) FROM ships")
        print(f"Total ships: {cursor.fetchone()[0]}")
        
        # Expected arrivals
        cursor.execute("SELECT COUNT(*) FROM expected_arrivals")
        print(f"Expected arrivals: {cursor.fetchone()[0]}")
        
        # Ships on port
        cursor.execute("SELECT COUNT(*) FROM ships_on_port")
        print(f"Ships on port: {cursor.fetchone()[0]}")
        
        # Ships off port
        cursor.execute("SELECT COUNT(*) FROM ships_off_port")
        print(f"Ships off port: {cursor.fetchone()[0]}")
        
        # Departures
        cursor.execute("SELECT COUNT(*) FROM ship_departures")
        print(f"Ship departures: {cursor.fetchone()[0]}")
        
        # Shipping agents
        cursor.execute("SELECT COUNT(*) FROM shipping_agents")
        print(f"Shipping agents: {cursor.fetchone()[0]}")
        
        # Date range
        cursor.execute("""
            SELECT MIN(DATE(scraped_at)), MAX(DATE(scraped_at))
            FROM expected_arrivals
        """)
        date_range = cursor.fetchone()
        if date_range[0]:
            print(f"\nData range: {date_range[0]} to {date_range[1]}")


def search_ships(args):
    """Search for ships"""
    db = DatabaseManager(args.db_path)
    
    with db as conn:
        ships = db.search_ships(args.query)
        
        if not ships:
            print(f"No ships found matching '{args.query}'")
            return
        
        print(f"\nFound {len(ships)} ships:\n")
        for ship in ships:
            print(f"- {ship['name']}")
            if ship['vessel_type']:
                print(f"  Type: {ship['vessel_type']}")
            if ship['flag']:
                print(f"  Flag: {ship['flag']}")
            print()


def ship_history(args):
    """Show ship history"""
    db = DatabaseManager(args.db_path)
    
    with db as conn:
        history = db.get_ship_history(args.ship_name)
        
        if not history:
            print(f"No history found for ship '{args.ship_name}'")
            return
        
        print(f"\nHistory for {args.ship_name}:\n")
        for event in history:
            print(f"[{event['scraped_at']}] {event['event_type']}")
            if 'event_date' in event and event['event_date']:
                print(f"  Date: {event['event_date']}")
            if 'cargo_type' in event and event['cargo_type']:
                print(f"  Cargo: {event['cargo_type']}")
            print()


def generate_report(args):
    """Generate analytics report"""
    db = DatabaseManager(args.db_path)
    analytics = ShippingAnalytics(db)
    
    report = analytics.generate_daily_report(args.date)
    
    print(f"\n=== Daily Report for {report['date']} ===\n")
    print(f"Expected Arrivals: {report['expected_arrivals']['count']}")
    print(f"  Import: {report['expected_arrivals']['total_import']} tons")
    print(f"  Export: {report['expected_arrivals']['total_export']} tons")
    print(f"Ships on Port: {report['ships_on_port']}")
    print(f"Ships off Port: {report['ships_off_port']}")
    print(f"Departures: {report['departures']}")
    
    if report['top_cargo_types']:
        print(f"\nTop Cargo Types:")
        for cargo in report['top_cargo_types']:
            print(f"  - {cargo['cargo_type']}: {cargo['count']}")
    
    if args.export:
        filename = args.export
        analytics.export_report_to_excel(report, filename)
        print(f"\n✓ Report exported to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Shipping Intelligence Database Management CLI'
    )
    parser.add_argument(
        '--db-path',
        default='shipping_intelligence.db',
        help='Path to database file (default: shipping_intelligence.db)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database schema')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from Excel files')
    import_parser.add_argument('--file', help='Specific Excel file to import')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for ships')
    search_parser.add_argument('query', help='Search query')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show ship history')
    history_parser.add_argument('ship_name', help='Ship name')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate daily report')
    report_parser.add_argument('--date', help='Date (YYYY-MM-DD), defaults to today')
    report_parser.add_argument('--export', help='Export to Excel file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'init': init_database,
        'import': import_data,
        'stats': show_stats,
        'search': search_ships,
        'history': ship_history,
        'report': generate_report
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()
