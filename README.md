# Shipping Data Scraper

This repository contains a Python script that scrapes publicly available shipping intelligence data using GitHub Actions for automation.

## 📊 Features:
- Automated data collection from shipping websites
- Excel file generation with structured data
- PDF document archival
- SQLite database for data persistence
- Scheduled execution via GitHub Actions

## 🗂️ Data Organization:
- Files organized in date-named folders
- Excel format for easy analysis
- PDF documents for reference
- Historical data tracking

## ⏰ Automation:
- Runs automatically on a daily schedule
- Manual execution available via GitHub Actions
- No server maintenance required

## 📁 Output Structure:
```
├── YYYY-MM-DD/
│   ├── data.xlsx
│   └── documents.pdf
└── database.db
```

## 🔧 Setup:
1. Fork or clone this repository
2. Enable GitHub Actions in repository settings
3. The workflow will run automatically on schedule

## 📈 Usage:
- Check the dated folders for daily data
- Download files as needed
- Access historical information from the database