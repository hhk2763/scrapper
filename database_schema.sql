-- Shipping Intelligence Database Schema
-- Comprehensive schema for shipping data startup

-- Ships master table
CREATE TABLE IF NOT EXISTS ships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    vessel_type TEXT,
    flag TEXT,
    imo_number TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipping agents table
CREATE TABLE IF NOT EXISTS shipping_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expected arrivals table (enhanced)
CREATE TABLE IF NOT EXISTS expected_arrivals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ship_id INTEGER,
    shipping_agent_id INTEGER,
    arrival_date TEXT,
    import_tons REAL,
    export_tons REAL,
    cargo_type TEXT,
    status TEXT DEFAULT 'expected',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_id) REFERENCES ships(id),
    FOREIGN KEY (shipping_agent_id) REFERENCES shipping_agents(id)
);

-- Ships off port table
CREATE TABLE IF NOT EXISTS ships_off_port (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ship_id INTEGER,
    vessel_type TEXT,
    flag TEXT,
    rotation TEXT,
    anchorage_date TEXT,
    remarks TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_id) REFERENCES ships(id)
);

-- Ship departures table
CREATE TABLE IF NOT EXISTS ship_departures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ship_id INTEGER,
    vessel_type TEXT,
    flag TEXT,
    rotation TEXT,
    departure_date TEXT,
    remarks TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_id) REFERENCES ships(id)
);

-- Ships on port table
CREATE TABLE IF NOT EXISTS ships_on_port (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ship_id INTEGER,
    vessel_type TEXT,
    flag TEXT,
    rotation TEXT,
    berth TEXT,
    arrival_date TEXT,
    remarks TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_id) REFERENCES ships(id)
);

-- Port operations table
CREATE TABLE IF NOT EXISTS port_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_date DATE,
    operation_type TEXT,
    description TEXT,
    metrics TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily tonnage table
CREATE TABLE IF NOT EXISTS daily_tonnage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date DATE,
    import_tonnage REAL,
    export_tonnage REAL,
    total_tonnage REAL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TEUS handling table
CREATE TABLE IF NOT EXISTS teus_handling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date DATE,
    import_teus INTEGER,
    export_teus INTEGER,
    total_teus INTEGER,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Berthing pre-plan table
CREATE TABLE IF NOT EXISTS berthing_preplans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ship_id INTEGER,
    planned_berth TEXT,
    planned_arrival TEXT,
    planned_departure TEXT,
    cargo_description TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_id) REFERENCES ships(id)
);

-- Cargo types reference table
CREATE TABLE IF NOT EXISTS cargo_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    description TEXT
);

-- Analytics: Daily summary table
CREATE TABLE IF NOT EXISTS daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_date DATE UNIQUE,
    total_ships_expected INTEGER DEFAULT 0,
    total_ships_off_port INTEGER DEFAULT 0,
    total_ships_on_port INTEGER DEFAULT 0,
    total_ships_departed INTEGER DEFAULT 0,
    total_import_tons REAL DEFAULT 0,
    total_export_tons REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ships_name ON ships(name);
CREATE INDEX IF NOT EXISTS idx_expected_arrivals_date ON expected_arrivals(arrival_date);
CREATE INDEX IF NOT EXISTS idx_departures_date ON ship_departures(departure_date);
CREATE INDEX IF NOT EXISTS idx_ships_on_port_berth ON ships_on_port(berth);
CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_summary(summary_date);
