#!/usr/bin/env python3
"""
Example Usage of Shipping Intelligence Platform
Demonstrates how to use the database and analytics modules
"""

from database_manager import DatabaseManager
from analytics import ShippingAnalytics
import json


def example_1_search_ships():
    """Example 1: Search for ships by name"""
    print("=" * 60)
    print("Example 1: Search for Ships")
    print("=" * 60)
    
    db = DatabaseManager()
    with db as conn:
        ships = db.search_ships("Marine")
        print(f"\nFound {len(ships)} ships matching 'Marine':")
        for ship in ships:
            print(f"  - {ship['name']} ({ship['vessel_type']})")


def example_2_get_ship_history():
    """Example 2: Get complete history of a specific ship"""
    print("\n" + "=" * 60)
    print("Example 2: Get Ship History")
    print("=" * 60)
    
    db = DatabaseManager()
    with db as conn:
        # Get a ship name from database
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM ships LIMIT 1")
        ship_name = cursor.fetchone()[0]
        
        history = db.get_ship_history(ship_name)
        print(f"\nHistory for '{ship_name}':")
        print(f"Total events: {len(history)}")
        
        if history:
            print("\nRecent events:")
            for event in history[:3]:
                print(f"  - {event['event_type']}: {event.get('event_date', 'N/A')}")


def example_3_daily_statistics():
    """Example 3: Get daily statistics"""
    print("\n" + "=" * 60)
    print("Example 3: Daily Statistics")
    print("=" * 60)
    
    db = DatabaseManager()
    with db as conn:
        stats = db.get_daily_statistics()
        print("\nToday's Statistics:")
        print(f"  Expected Arrivals: {stats['expected_arrivals']}")
        print(f"  Import Tonnage: {stats['import_tons']:,.0f} tons")
        print(f"  Export Tonnage: {stats['export_tons']:,.0f} tons")
        print(f"  Ships Off Port: {stats['ships_off_port']}")
        print(f"  Ships On Port: {stats['ships_on_port']}")
        print(f"  Departures: {stats['ship_departures']}")


def example_4_cargo_analytics():
    """Example 4: Analyze cargo types"""
    print("\n" + "=" * 60)
    print("Example 4: Cargo Type Analytics")
    print("=" * 60)
    
    db = DatabaseManager()
    analytics = ShippingAnalytics(db)
    
    cargo_dist = analytics.get_cargo_distribution()
    print(f"\nTotal cargo types: {cargo_dist['total_types']}")
    print("\nTop 5 cargo types by shipment count:")
    
    for i, cargo in enumerate(cargo_dist['cargo_types'][:5], 1):
        print(f"{i}. {cargo['cargo_type']}")
        print(f"   Shipments: {cargo['shipment_count']}")
        print(f"   Avg Import: {cargo['avg_import_tons']:,.0f} tons")
        print(f"   Avg Export: {cargo['avg_export_tons']:,.0f} tons")


def example_5_top_agents():
    """Example 5: Get top shipping agents"""
    print("\n" + "=" * 60)
    print("Example 5: Top Shipping Agents")
    print("=" * 60)
    
    db = DatabaseManager()
    analytics = ShippingAnalytics(db)
    
    agents = analytics.get_top_shipping_agents(limit=5)
    print("\nTop 5 shipping agents by activity:")
    
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent['name']}")
        print(f"   Total Shipments: {agent['total_shipments']}")
        print(f"   Unique Ships: {agent['unique_ships']}")
        print(f"   Total Import: {agent['total_import']:,.0f} tons")
        print(f"   Total Export: {agent['total_export']:,.0f} tons")


def example_6_traffic_trends():
    """Example 6: Analyze traffic trends"""
    print("\n" + "=" * 60)
    print("Example 6: Port Traffic Trends")
    print("=" * 60)
    
    db = DatabaseManager()
    analytics = ShippingAnalytics(db)
    
    trends = analytics.get_traffic_trends(days=7)
    print(f"\nTraffic analysis for last {trends['period_days']} days:")
    print(f"Average daily ships: {trends['average_daily_ships']:.1f}")
    
    print("\nDaily breakdown:")
    for trend in trends['trends']:
        print(f"  {trend['date']}: {trend['unique_ships']} ships, "
              f"{trend['total_activities']} activities")


def example_7_active_ships():
    """Example 7: Get currently active ships"""
    print("\n" + "=" * 60)
    print("Example 7: Currently Active Ships")
    print("=" * 60)
    
    db = DatabaseManager()
    with db as conn:
        active_ships = db.get_active_ships()
        print(f"\nCurrently active ships: {len(active_ships)}")
        
        # Group by status
        on_port = [s for s in active_ships if s['status'] == 'on_port']
        off_port = [s for s in active_ships if s['status'] == 'off_port']
        
        print(f"  - On Port: {len(on_port)}")
        print(f"  - Off Port: {len(off_port)}")
        
        if off_port:
            print("\nSample ships off port:")
            for ship in off_port[:3]:
                print(f"  - {ship['name']} ({ship['vessel_type']})")


def example_8_api_integration():
    """Example 8: How to integrate with the API"""
    print("\n" + "=" * 60)
    print("Example 8: API Integration Example")
    print("=" * 60)
    
    print("\nTo use the REST API, start the server:")
    print("  $ python api_server.py")
    print("\nThen make HTTP requests:")
    print("\n# Get statistics")
    print("  curl http://localhost:5000/api/statistics")
    print("\n# Search ships")
    print("  curl http://localhost:5000/api/ships/search?q=Marine")
    print("\n# Get arrivals")
    print("  curl http://localhost:5000/api/arrivals?limit=10")
    
    print("\nPython requests example:")
    print("""
import requests

# Get statistics
response = requests.get('http://localhost:5000/api/statistics')
stats = response.json()
print(f"Expected arrivals: {stats['expected_arrivals']}")

# Search ships
response = requests.get(
    'http://localhost:5000/api/ships/search',
    params={'q': 'Marine'}
)
ships = response.json()
for ship in ships['ships']:
    print(ship['name'])
    """)


def example_9_custom_query():
    """Example 9: Custom database queries"""
    print("\n" + "=" * 60)
    print("Example 9: Custom Database Query")
    print("=" * 60)
    
    db = DatabaseManager()
    with db as conn:
        cursor = conn.cursor()
        
        # Custom query: Ships with highest export tonnage
        cursor.execute("""
            SELECT 
                s.name,
                s.vessel_type,
                SUM(ea.export_tons) as total_export
            FROM ships s
            JOIN expected_arrivals ea ON s.id = ea.ship_id
            WHERE ea.export_tons > 0
            GROUP BY s.id, s.name, s.vessel_type
            ORDER BY total_export DESC
            LIMIT 5
        """)
        
        print("\nTop 5 ships by export tonnage:")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]}): {row[2]:,.0f} tons")


def example_10_generate_report():
    """Example 10: Generate and export report"""
    print("\n" + "=" * 60)
    print("Example 10: Generate Excel Report")
    print("=" * 60)
    
    db = DatabaseManager()
    analytics = ShippingAnalytics(db)
    
    report = analytics.generate_daily_report()
    filename = "custom_report_example.xlsx"
    analytics.export_report_to_excel(report, filename)
    
    print(f"\n✓ Report generated: {filename}")
    print(f"  Date: {report['date']}")
    print(f"  Expected Arrivals: {report['expected_arrivals']['count']}")
    print(f"  Import: {report['expected_arrivals']['total_import']:,.0f} tons")
    print(f"  Export: {report['expected_arrivals']['total_export']:,.0f} tons")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Shipping Intelligence Platform - Usage Examples")
    print("=" * 60)
    
    examples = [
        example_1_search_ships,
        example_2_get_ship_history,
        example_3_daily_statistics,
        example_4_cargo_analytics,
        example_5_top_agents,
        example_6_traffic_trends,
        example_7_active_ships,
        example_8_api_integration,
        example_9_custom_query,
        example_10_generate_report
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nFor more information, see STARTUP_GUIDE.md")


if __name__ == "__main__":
    main()
