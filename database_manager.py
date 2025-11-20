"""
Database Manager for Shipping Intelligence Startup
Handles all database operations, migrations, and data access
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import os


class DatabaseManager:
    """Manages database connections and operations for shipping intelligence data"""
    
    def __init__(self, db_path: str = "shipping_intelligence.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def __enter__(self):
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.close()
    
    def initialize_schema(self, schema_file: str = "database_schema.sql"):
        """Initialize database with schema from SQL file"""
        with self.connect() as conn:
            with open(schema_file, 'r') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
        print(f"Database schema initialized from {schema_file}")
    
    def get_or_create_ship(self, ship_name: str, vessel_type: str = None) -> int:
        """Get ship ID or create new ship record"""
        cursor = self.conn.cursor()
        
        # Try to find existing ship
        cursor.execute("SELECT id FROM ships WHERE name = ?", (ship_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new ship
        cursor.execute(
            "INSERT INTO ships (name, vessel_type) VALUES (?, ?)",
            (ship_name, vessel_type)
        )
        return cursor.lastrowid
    
    def get_or_create_shipping_agent(self, agent_name: str) -> int:
        """Get shipping agent ID or create new agent record"""
        cursor = self.conn.cursor()
        
        # Try to find existing agent
        cursor.execute("SELECT id FROM shipping_agents WHERE name = ?", (agent_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new agent
        cursor.execute(
            "INSERT INTO shipping_agents (name) VALUES (?)",
            (agent_name,)
        )
        return cursor.lastrowid
    
    def insert_expected_arrival(self, data: Dict[str, Any]) -> int:
        """Insert expected arrival record"""
        cursor = self.conn.cursor()
        
        ship_id = self.get_or_create_ship(data.get('ship_name'), data.get('vessel_type'))
        agent_id = self.get_or_create_shipping_agent(data.get('shipping_agent', ''))
        
        cursor.execute("""
            INSERT INTO expected_arrivals 
            (ship_id, shipping_agent_id, arrival_date, import_tons, export_tons, cargo_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ship_id,
            agent_id,
            data.get('arrival_date'),
            data.get('import_tons'),
            data.get('export_tons'),
            data.get('cargo_type')
        ))
        return cursor.lastrowid
    
    def insert_ship_off_port(self, data: Dict[str, Any]) -> int:
        """Insert ship off port record"""
        cursor = self.conn.cursor()
        
        ship_id = self.get_or_create_ship(data.get('ship_name'), data.get('vessel_type'))
        
        cursor.execute("""
            INSERT INTO ships_off_port 
            (ship_id, vessel_type, flag, rotation, anchorage_date, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ship_id,
            data.get('vessel_type'),
            data.get('flag'),
            data.get('rotation'),
            data.get('anchorage_date'),
            data.get('remarks')
        ))
        return cursor.lastrowid
    
    def insert_ship_departure(self, data: Dict[str, Any]) -> int:
        """Insert ship departure record"""
        cursor = self.conn.cursor()
        
        ship_id = self.get_or_create_ship(data.get('ship_name'), data.get('vessel_type'))
        
        cursor.execute("""
            INSERT INTO ship_departures 
            (ship_id, vessel_type, flag, rotation, departure_date, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ship_id,
            data.get('vessel_type'),
            data.get('flag'),
            data.get('rotation'),
            data.get('departure_date'),
            data.get('remarks')
        ))
        return cursor.lastrowid
    
    def insert_ship_on_port(self, data: Dict[str, Any]) -> int:
        """Insert ship on port record"""
        cursor = self.conn.cursor()
        
        ship_id = self.get_or_create_ship(data.get('ship_name'), data.get('vessel_type'))
        
        cursor.execute("""
            INSERT INTO ships_on_port 
            (ship_id, vessel_type, flag, rotation, berth, arrival_date, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ship_id,
            data.get('vessel_type'),
            data.get('flag'),
            data.get('rotation'),
            data.get('berth'),
            data.get('arrival_date'),
            data.get('remarks')
        ))
        return cursor.lastrowid
    
    def get_daily_statistics(self, date: str = None) -> Dict[str, Any]:
        """Get daily statistics for a specific date or today"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Count expected arrivals
        cursor.execute("""
            SELECT COUNT(*) as count, 
                   SUM(import_tons) as total_import, 
                   SUM(export_tons) as total_export
            FROM expected_arrivals 
            WHERE DATE(scraped_at) = ?
        """, (date,))
        result = cursor.fetchone()
        stats['expected_arrivals'] = result[0]
        stats['import_tons'] = result[1] or 0
        stats['export_tons'] = result[2] or 0
        
        # Count ships off port
        cursor.execute("""
            SELECT COUNT(*) FROM ships_off_port 
            WHERE DATE(scraped_at) = ?
        """, (date,))
        stats['ships_off_port'] = cursor.fetchone()[0]
        
        # Count ships on port
        cursor.execute("""
            SELECT COUNT(*) FROM ships_on_port 
            WHERE DATE(scraped_at) = ?
        """, (date,))
        stats['ships_on_port'] = cursor.fetchone()[0]
        
        # Count departures
        cursor.execute("""
            SELECT COUNT(*) FROM ship_departures 
            WHERE DATE(scraped_at) = ?
        """, (date,))
        stats['ship_departures'] = cursor.fetchone()[0]
        
        return stats
    
    def get_ship_history(self, ship_name: str) -> List[Dict[str, Any]]:
        """Get complete history of a ship"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM ships WHERE name = ?", (ship_name,))
        result = cursor.fetchone()
        
        if not result:
            return []
        
        ship_id = result[0]
        history = []
        
        # Get arrivals
        cursor.execute("""
            SELECT 'expected_arrival' as event_type, arrival_date as event_date, 
                   cargo_type, scraped_at
            FROM expected_arrivals 
            WHERE ship_id = ?
            ORDER BY scraped_at DESC
        """, (ship_id,))
        history.extend([dict(row) for row in cursor.fetchall()])
        
        # Get departures
        cursor.execute("""
            SELECT 'departure' as event_type, departure_date as event_date, 
                   remarks, scraped_at
            FROM ship_departures 
            WHERE ship_id = ?
            ORDER BY scraped_at DESC
        """, (ship_id,))
        history.extend([dict(row) for row in cursor.fetchall()])
        
        return sorted(history, key=lambda x: x['scraped_at'], reverse=True)
    
    def search_ships(self, query: str) -> List[Dict[str, Any]]:
        """Search for ships by name"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, name, vessel_type, flag, imo_number
            FROM ships 
            WHERE name LIKE ?
            ORDER BY name
        """, (f'%{query}%',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_active_ships(self) -> List[Dict[str, Any]]:
        """Get list of currently active ships (on port or off port)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT s.id, s.name, s.vessel_type, s.flag,
                   'on_port' as status, sop.berth, sop.scraped_at
            FROM ships s
            JOIN ships_on_port sop ON s.id = sop.ship_id
            WHERE DATE(sop.scraped_at) = DATE('now')
            
            UNION
            
            SELECT DISTINCT s.id, s.name, s.vessel_type, s.flag,
                   'off_port' as status, NULL as berth, sofp.scraped_at
            FROM ships s
            JOIN ships_off_port sofp ON s.id = sofp.ship_id
            WHERE DATE(sofp.scraped_at) = DATE('now')
            
            ORDER BY scraped_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
