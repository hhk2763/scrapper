"""
Analytics and Reporting Module for Shipping Intelligence Startup
Generates insights and reports from shipping data
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from database_manager import DatabaseManager


class ShippingAnalytics:
    """Provides analytics and insights from shipping data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_traffic_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get port traffic trends over specified days"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(scraped_at) as date,
                    COUNT(DISTINCT ship_id) as unique_ships,
                    COUNT(*) as total_activities
                FROM (
                    SELECT ship_id, scraped_at FROM expected_arrivals
                    UNION ALL
                    SELECT ship_id, scraped_at FROM ship_departures
                    UNION ALL
                    SELECT ship_id, scraped_at FROM ships_on_port
                    UNION ALL
                    SELECT ship_id, scraped_at FROM ships_off_port
                )
                WHERE DATE(scraped_at) >= DATE('now', '-' || ? || ' days')
                GROUP BY DATE(scraped_at)
                ORDER BY date DESC
            """, (days,))
            
            trends = [dict(row) for row in cursor.fetchall()]
            
            return {
                'period_days': days,
                'trends': trends,
                'average_daily_ships': sum(t['unique_ships'] for t in trends) / len(trends) if trends else 0
            }
    
    def get_cargo_distribution(self) -> Dict[str, Any]:
        """Get distribution of cargo types"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    cargo_type,
                    COUNT(*) as shipment_count,
                    SUM(import_tons) as total_import_tons,
                    SUM(export_tons) as total_export_tons,
                    AVG(import_tons) as avg_import_tons,
                    AVG(export_tons) as avg_export_tons
                FROM expected_arrivals
                WHERE cargo_type IS NOT NULL
                GROUP BY cargo_type
                ORDER BY shipment_count DESC
            """)
            
            distribution = [dict(row) for row in cursor.fetchall()]
            
            return {
                'cargo_types': distribution,
                'total_types': len(distribution)
            }
    
    def get_top_shipping_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top shipping agents by activity"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    sa.name,
                    COUNT(DISTINCT ea.ship_id) as unique_ships,
                    COUNT(*) as total_shipments,
                    SUM(ea.import_tons) as total_import,
                    SUM(ea.export_tons) as total_export
                FROM shipping_agents sa
                JOIN expected_arrivals ea ON sa.id = ea.shipping_agent_id
                GROUP BY sa.id, sa.name
                ORDER BY total_shipments DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_busiest_berths(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get busiest berths at the port"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    berth,
                    COUNT(*) as usage_count,
                    COUNT(DISTINCT ship_id) as unique_ships
                FROM ships_on_port
                WHERE berth IS NOT NULL 
                    AND berth != ''
                    AND DATE(scraped_at) >= DATE('now', '-' || ? || ' days')
                GROUP BY berth
                ORDER BY usage_count DESC
            """, (days,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_vessel_type_distribution(self) -> Dict[str, Any]:
        """Get distribution of vessel types"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    vessel_type,
                    COUNT(*) as count
                FROM ships
                WHERE vessel_type IS NOT NULL
                GROUP BY vessel_type
                ORDER BY count DESC
            """)
            
            distribution = [dict(row) for row in cursor.fetchall()]
            
            return {
                'vessel_types': distribution,
                'total_types': len(distribution),
                'total_ships': sum(v['count'] for v in distribution)
            }
    
    def get_flag_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics by ship flag/country"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    flag,
                    COUNT(*) as ship_count
                FROM ships
                WHERE flag IS NOT NULL AND flag != ''
                GROUP BY flag
                ORDER BY ship_count DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """Generate comprehensive daily report"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            report = {
                'date': date,
                'generated_at': datetime.now().isoformat()
            }
            
            # Expected arrivals summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(import_tons) as total_import,
                    SUM(export_tons) as total_export,
                    COUNT(DISTINCT cargo_type) as cargo_types
                FROM expected_arrivals
                WHERE DATE(scraped_at) = ?
            """, (date,))
            arrivals = dict(cursor.fetchone())
            report['expected_arrivals'] = arrivals
            
            # Ships on port
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM ships_on_port
                WHERE DATE(scraped_at) = ?
            """, (date,))
            report['ships_on_port'] = cursor.fetchone()[0]
            
            # Ships off port
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM ships_off_port
                WHERE DATE(scraped_at) = ?
            """, (date,))
            report['ships_off_port'] = cursor.fetchone()[0]
            
            # Departures
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM ship_departures
                WHERE DATE(scraped_at) = ?
            """, (date,))
            report['departures'] = cursor.fetchone()[0]
            
            # Top cargo types for the day
            cursor.execute("""
                SELECT cargo_type, COUNT(*) as count
                FROM expected_arrivals
                WHERE DATE(scraped_at) = ? AND cargo_type IS NOT NULL
                GROUP BY cargo_type
                ORDER BY count DESC
                LIMIT 5
            """, (date,))
            report['top_cargo_types'] = [dict(row) for row in cursor.fetchall()]
            
            return report
    
    def export_report_to_excel(self, report: Dict[str, Any], filename: str):
        """Export report to Excel file"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([{
                'Date': report['date'],
                'Expected Arrivals': report['expected_arrivals']['count'],
                'Ships On Port': report['ships_on_port'],
                'Ships Off Port': report['ships_off_port'],
                'Departures': report['departures'],
                'Total Import (tons)': report['expected_arrivals']['total_import'],
                'Total Export (tons)': report['expected_arrivals']['total_export']
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Top cargo types
            if report['top_cargo_types']:
                cargo_df = pd.DataFrame(report['top_cargo_types'])
                cargo_df.to_excel(writer, sheet_name='Top Cargo Types', index=False)
        
        print(f"Report exported to {filename}")
    
    def get_ship_frequency_analysis(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most frequent ships in the database"""
        with self.db_manager as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    s.name,
                    s.vessel_type,
                    s.flag,
                    COUNT(DISTINCT ea.id) as arrival_count,
                    COUNT(DISTINCT sd.id) as departure_count,
                    MAX(ea.scraped_at) as last_seen
                FROM ships s
                LEFT JOIN expected_arrivals ea ON s.id = ea.ship_id
                LEFT JOIN ship_departures sd ON s.id = sd.ship_id
                GROUP BY s.id, s.name, s.vessel_type, s.flag
                HAVING arrival_count > 0 OR departure_count > 0
                ORDER BY arrival_count + departure_count DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]


def main():
    """Main function to demonstrate analytics"""
    db_manager = DatabaseManager()
    analytics = ShippingAnalytics(db_manager)
    
    print("=== Shipping Intelligence Analytics ===\n")
    
    # Traffic trends
    print("1. Traffic Trends (Last 7 Days)")
    trends = analytics.get_traffic_trends(days=7)
    print(f"Average daily ships: {trends['average_daily_ships']:.1f}")
    for trend in trends['trends'][:5]:
        print(f"  {trend['date']}: {trend['unique_ships']} ships, {trend['total_activities']} activities")
    
    # Cargo distribution
    print("\n2. Cargo Distribution")
    cargo = analytics.get_cargo_distribution()
    print(f"Total cargo types: {cargo['total_types']}")
    for c in cargo['cargo_types'][:5]:
        print(f"  {c['cargo_type']}: {c['shipment_count']} shipments")
    
    # Top shipping agents
    print("\n3. Top Shipping Agents")
    agents = analytics.get_top_shipping_agents(limit=5)
    for agent in agents:
        print(f"  {agent['name']}: {agent['total_shipments']} shipments")
    
    # Vessel type distribution
    print("\n4. Vessel Type Distribution")
    vessels = analytics.get_vessel_type_distribution()
    print(f"Total vessel types: {vessels['total_types']}")
    for v in vessels['vessel_types'][:5]:
        print(f"  {v['vessel_type']}: {v['count']} ships")
    
    # Daily report
    print("\n5. Today's Report")
    report = analytics.generate_daily_report()
    print(f"Date: {report['date']}")
    print(f"Expected arrivals: {report['expected_arrivals']['count']}")
    print(f"Ships on port: {report['ships_on_port']}")
    print(f"Ships off port: {report['ships_off_port']}")
    print(f"Departures: {report['departures']}")
    
    # Export report
    report_filename = f"shipping_report_{report['date']}.xlsx"
    analytics.export_report_to_excel(report, report_filename)


if __name__ == "__main__":
    main()
