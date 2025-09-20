# KPT Data Scraper

This repository automatically scrapes shipping intelligence data from Karachi Port Trust (KPT) website daily using GitHub Actions.

## 📊 What it scrapes:
- Expected Arrivals
- Ships Off Port  
- Ship Departures
- Ships On Port
- Related PDF documents

## 🗂️ Data Storage:
- Excel files saved in date-named folders (e.g., `2025-09-20/`)
- PDF documents downloaded to the same folders
- SQLite database (`shipping_intelligence.db`) for historical data

## ⏰ Schedule:
- Runs automatically every day at 12:00 AM UTC
- Can be triggered manually from GitHub Actions tab

## 📁 Folder Structure:
```
├── 2025-09-20/
│   ├── expected_arrival.xlsx
│   ├── 2025-09-20_berthing-pre-plan.pdf
│   ├── 2025-09-20_daily-tonnage.pdf
│   ├── 2025-09-20_port-operations.pdf
│   └── 2025-09-20_teus-handling.pdf
├── 2025-09-21/
│   └── ... (next day's data)
└── shipping_intelligence.db
```

## 🔧 Setup:
1. Push this repository to GitHub
2. Enable Actions in repository settings
3. The workflow will run automatically daily

## 📈 Viewing Data:
- Browse the date folders for daily data
- Download the Excel files or PDFs as needed
- Access historical data from the SQLite database