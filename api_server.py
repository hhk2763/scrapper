"""
REST API Server for Shipping Intelligence Startup
Provides API endpoints for accessing shipping data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from database_manager import DatabaseManager
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

db_manager = DatabaseManager()


@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'name': 'Shipping Intelligence API',
        'version': '1.0.0',
        'description': 'API for accessing Karachi Port shipping data',
        'endpoints': {
            '/api/ships': 'List all ships',
            '/api/ships/<name>': 'Get ship details and history',
            '/api/ships/search?q=<query>': 'Search ships by name',
            '/api/ships/active': 'Get currently active ships',
            '/api/statistics': 'Get daily statistics',
            '/api/statistics/<date>': 'Get statistics for specific date',
            '/api/arrivals': 'Get expected arrivals',
            '/api/departures': 'Get ship departures',
            '/api/ships-on-port': 'Get ships currently on port',
            '/api/ships-off-port': 'Get ships off port',
            '/api/agents': 'Get shipping agents'
        }
    })


@app.route('/api/ships', methods=['GET'])
def list_ships():
    """List all ships with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    
    with db_manager as conn:
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM ships")
        total = cursor.fetchone()[0]
        
        # Get paginated results
        cursor.execute("""
            SELECT id, name, vessel_type, flag, imo_number, created_at
            FROM ships
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        ships = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'total': total,
            'page': page,
            'per_page': per_page,
            'ships': ships
        })


@app.route('/api/ships/<string:ship_name>', methods=['GET'])
def get_ship(ship_name):
    """Get ship details and history"""
    with db_manager as conn:
        cursor = conn.cursor()
        
        # Get ship details
        cursor.execute("""
            SELECT id, name, vessel_type, flag, imo_number, created_at, updated_at
            FROM ships
            WHERE name = ?
        """, (ship_name,))
        
        ship = cursor.fetchone()
        
        if not ship:
            return jsonify({'error': 'Ship not found'}), 404
        
        ship_dict = dict(ship)
        
        # Get history
        history = db_manager.get_ship_history(ship_name)
        ship_dict['history'] = history
        
        return jsonify(ship_dict)


@app.route('/api/ships/search', methods=['GET'])
def search_ships():
    """Search ships by name"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    with db_manager as conn:
        ships = db_manager.search_ships(query)
        return jsonify({
            'query': query,
            'count': len(ships),
            'ships': ships
        })


@app.route('/api/ships/active', methods=['GET'])
def get_active_ships():
    """Get currently active ships"""
    with db_manager as conn:
        ships = db_manager.get_active_ships()
        return jsonify({
            'count': len(ships),
            'ships': ships
        })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get today's statistics"""
    with db_manager as conn:
        stats = db_manager.get_daily_statistics()
        return jsonify(stats)


@app.route('/api/statistics/<string:date>', methods=['GET'])
def get_statistics_by_date(date):
    """Get statistics for a specific date (YYYY-MM-DD)"""
    with db_manager as conn:
        stats = db_manager.get_daily_statistics(date)
        return jsonify({
            'date': date,
            'statistics': stats
        })


@app.route('/api/arrivals', methods=['GET'])
def get_expected_arrivals():
    """Get expected arrivals"""
    limit = request.args.get('limit', 100, type=int)
    
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                ea.id,
                s.name as ship_name,
                s.vessel_type,
                sa.name as shipping_agent,
                ea.arrival_date,
                ea.import_tons,
                ea.export_tons,
                ea.cargo_type,
                ea.status,
                ea.scraped_at
            FROM expected_arrivals ea
            JOIN ships s ON ea.ship_id = s.id
            LEFT JOIN shipping_agents sa ON ea.shipping_agent_id = sa.id
            ORDER BY ea.scraped_at DESC
            LIMIT ?
        """, (limit,))
        
        arrivals = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'count': len(arrivals),
            'arrivals': arrivals
        })


@app.route('/api/departures', methods=['GET'])
def get_departures():
    """Get ship departures"""
    limit = request.args.get('limit', 100, type=int)
    
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sd.id,
                s.name as ship_name,
                sd.vessel_type,
                sd.flag,
                sd.rotation,
                sd.departure_date,
                sd.remarks,
                sd.scraped_at
            FROM ship_departures sd
            JOIN ships s ON sd.ship_id = s.id
            ORDER BY sd.scraped_at DESC
            LIMIT ?
        """, (limit,))
        
        departures = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'count': len(departures),
            'departures': departures
        })


@app.route('/api/ships-on-port', methods=['GET'])
def get_ships_on_port():
    """Get ships currently on port"""
    limit = request.args.get('limit', 100, type=int)
    
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sop.id,
                s.name as ship_name,
                sop.vessel_type,
                sop.flag,
                sop.rotation,
                sop.berth,
                sop.arrival_date,
                sop.remarks,
                sop.scraped_at
            FROM ships_on_port sop
            JOIN ships s ON sop.ship_id = s.id
            ORDER BY sop.scraped_at DESC
            LIMIT ?
        """, (limit,))
        
        ships = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'count': len(ships),
            'ships': ships
        })


@app.route('/api/ships-off-port', methods=['GET'])
def get_ships_off_port():
    """Get ships off port"""
    limit = request.args.get('limit', 100, type=int)
    
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sofp.id,
                s.name as ship_name,
                sofp.vessel_type,
                sofp.flag,
                sofp.rotation,
                sofp.anchorage_date,
                sofp.remarks,
                sofp.scraped_at
            FROM ships_off_port sofp
            JOIN ships s ON sofp.ship_id = s.id
            ORDER BY sofp.scraped_at DESC
            LIMIT ?
        """, (limit,))
        
        ships = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'count': len(ships),
            'ships': ships
        })


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all shipping agents"""
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, contact_info, created_at
            FROM shipping_agents
            ORDER BY name
        """)
        
        agents = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'count': len(agents),
            'agents': agents
        })


@app.route('/api/analytics/cargo-types', methods=['GET'])
def get_cargo_type_analytics():
    """Get analytics by cargo type"""
    with db_manager as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                cargo_type,
                COUNT(*) as count,
                SUM(import_tons) as total_import,
                SUM(export_tons) as total_export
            FROM expected_arrivals
            WHERE cargo_type IS NOT NULL
            GROUP BY cargo_type
            ORDER BY count DESC
        """)
        
        analytics = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'cargo_types': analytics
        })


@app.route('/api/analytics/vessel-types', methods=['GET'])
def get_vessel_type_analytics():
    """Get analytics by vessel type"""
    with db_manager as conn:
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
        
        analytics = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'vessel_types': analytics
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
