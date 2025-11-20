# Shipping Intelligence Platform 🚢

A complete database-driven startup infrastructure for shipping intelligence data. This system automatically scrapes shipping data from Karachi Port Trust (KPT) and provides a comprehensive database, REST API, and analytics platform for maritime business intelligence.

## 🚀 Startup Features

### Data Collection
- Automated data scraping from KPT website
- Daily scheduled execution via GitHub Actions
- Excel and PDF document archival
- Historical data tracking (60+ days of data)

### Database Infrastructure
- Normalized SQLite database schema
- 300+ ships tracked
- 1800+ expected arrivals recorded
- 67+ shipping agents
- 11+ cargo types
- Efficient indexing for fast queries

### REST API
- **Flask-based RESTful API** for data access
- 10+ endpoints for ships, arrivals, departures, analytics
- Search and filtering capabilities
- Pagination support
- CORS enabled for web clients

### Analytics & Reporting
- Traffic trends and patterns
- Cargo distribution analysis
- Top shipping agents ranking
- Vessel type statistics
- Excel report generation
- Daily summary reports

### CLI Tools
- Database initialization and management
- Data import and migration
- Search and query tools
- Report generation

## 📊 Quick Start

### 1. Setup Database
```bash
pip install -r requirements.txt
python cli.py init
python cli.py import
```

### 2. Start API Server
```bash
python api_server.py
# Server runs on http://localhost:5000
```

### 3. Use CLI Tools
```bash
python cli.py stats                    # Show statistics
python cli.py search "Marine"          # Search ships
python cli.py history "Ship Name"      # Get ship history
python cli.py report --date 2025-11-20 # Generate report
```

## 🔗 API Endpoints

- `GET /api/ships` - List all ships
- `GET /api/ships/<name>` - Get ship details
- `GET /api/ships/search?q=<query>` - Search ships
- `GET /api/arrivals` - Expected arrivals
- `GET /api/statistics` - Daily statistics
- `GET /api/analytics/cargo-types` - Cargo analytics

[See STARTUP_GUIDE.md for complete API documentation]

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

## 💼 Business Applications

- **Port Logistics** - Real-time vessel tracking
- **Supply Chain** - Cargo flow analytics  
- **Maritime Insurance** - Risk assessment data
- **Trade Intelligence** - Import/export patterns
- **Compliance Reporting** - Regulatory reports

## 📁 Project Structure
```
├── scrape_kpt.py           # Data scraper
├── database_schema.sql     # Database schema
├── database_manager.py     # Database operations
├── data_ingestion.py       # Data import pipeline
├── api_server.py           # REST API server
├── analytics.py            # Analytics & reporting
├── cli.py                  # Command-line tools
├── STARTUP_GUIDE.md        # Comprehensive startup guide
├── Dockerfile              # Container configuration
└── YYYY-MM-DD/             # Daily data folders
    ├── expected_arrival.xlsx
    └── *.pdf
```

## 📖 Documentation

- **[STARTUP_GUIDE.md](STARTUP_GUIDE.md)** - Complete startup documentation
  - Architecture overview
  - API reference
  - Monetization strategies
  - Deployment guides
  - Scaling roadmap

## 🔧 Tech Stack

- **Python 3.11+** - Core language
- **Flask** - REST API framework
- **SQLite** - Database (upgradeable to PostgreSQL)
- **Pandas** - Data processing
- **BeautifulSoup** - Web scraping
- **Docker** - Containerization

## ⚡ Performance

- 1800+ records imported in ~60 seconds
- Sub-second API response times
- Efficient database queries with indexes
- Scalable architecture

## 📈 Data Stats

- **Ships tracked**: 304+
- **Expected arrivals**: 1850+
- **Shipping agents**: 67+
- **Cargo types**: 11+
- **Historical data**: 60+ days
- **Daily updates**: Automatic

## 🎯 Next Steps

1. Explore the API endpoints
2. Read STARTUP_GUIDE.md for business strategy
3. Customize analytics for your use case
4. Deploy to production
5. Integrate with your applications

---

**Built for the maritime industry** 🌊