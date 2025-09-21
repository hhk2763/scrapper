BERTHING_PRE_PLAN_URL = "https://kpt.gov.pk/pages/80/berthing-pre-plan"
DAILY_TONNAGE_URL = "https://kpt.gov.pk/pages/78/daily-tonnage"
import pandas as pd
from pypdf import PdfReader

def pdf_to_excel_sheet(pdf_path, excel_path, sheet_name):
    """
    Extract text from PDF using PyPDF and save to a new sheet in Excel.
    Each page's text will be a row in the sheet.
    """
    try:
        reader = PdfReader(pdf_path)
        data = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    data.append([line])
        if data:
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df = pd.DataFrame(data, columns=["Text"])
                writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"PDF text from {pdf_path} added to {excel_path} as sheet '{sheet_name}' (PyPDF)")
        else:
            print(f"No text found in {pdf_path} (PyPDF)")
    except Exception as e:
        print(f"PyPDF failed for {pdf_path}: {e}")
import os
from datetime import datetime
PORT_OPERATIONS_URL = "https://kpt.gov.pk/pages/79/port-operations"
TEUS_HANDLING_URL = "https://kpt.gov.pk/pages/77/teus-handling"
# Create a folder named with today's date (Pakistani timezone)
pk_tz = pytz.timezone('Asia/Karachi')
pk_now = datetime.now(pk_tz)
today_folder = pk_now.strftime('%Y-%m-%d_%H-%M-%S')
os.makedirs(today_folder, exist_ok=True)
today_str = today_folder
def download_pdfs_and_convert():
    # Download from Berthing Pre Plan page
    bpp_response = requests.get(BERTHING_PRE_PLAN_URL)
    bpp_soup = BeautifulSoup(bpp_response.text, 'html.parser')
    bpp_links = bpp_soup.find_all('a', href=True)
    for link in bpp_links:
        href = link['href']
        if href.lower().endswith('.pdf') or 'rwcgi60.exe' in href:
            if not href.startswith('http'):
                file_url = 'https://kpt.gov.pk' + href if href.startswith('/') else href
            else:
                file_url = href
            file_name = f"{today_str}_berthing-pre-plan.pdf"
            file_path = os.path.join(today_folder, file_name)
            print(f"Downloading {file_url} to {file_path}")
            try:
                file_resp = requests.get(file_url)
                with open(file_path, 'wb') as f:
                    f.write(file_resp.content)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")
    # Download from Daily Tonnage page
    daily_response = requests.get(DAILY_TONNAGE_URL)
    daily_soup = BeautifulSoup(daily_response.text, 'html.parser')
    daily_links = daily_soup.find_all('a', href=True)
    for link in daily_links:
        href = link['href']
        if href.lower().endswith('.pdf') or 'rwcgi60.exe' in href:
            if not href.startswith('http'):
                file_url = 'https://kpt.gov.pk' + href if href.startswith('/') else href
            else:
                file_url = href
            file_name = f"{today_str}_daily-tonnage.pdf"
            file_path = os.path.join(today_folder, file_name)
            print(f"Downloading {file_url} to {file_path}")
            try:
                file_resp = requests.get(file_url)
                with open(file_path, 'wb') as f:
                    f.write(file_resp.content)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")
    # Folder already created above

    # Download from Port Operations page
    response = requests.get(PORT_OPERATIONS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if href.lower().endswith('.pdf') or 'rwcgi60.exe' in href:
            if not href.startswith('http'):
                file_url = 'https://kpt.gov.pk' + href if href.startswith('/') else href
            else:
                file_url = href
            # Use context-based naming for rwcgi60.exe links
            if 'rwcgi60.exe' in href:
                file_name = f"{today_str}_port-operations.pdf"
            else:
                base_name = file_url.split('/')[-1].split('?')[0] or 'downloaded_file.pdf'
                file_name = f"{today_str}_{base_name}"
            file_path = os.path.join(today_folder, file_name)
            print(f"Downloading {file_url} to {file_path}")
            try:
                file_resp = requests.get(file_url)
                with open(file_path, 'wb') as f:
                    f.write(file_resp.content)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")

    # Download from TEUS Handling page
    teus_response = requests.get(TEUS_HANDLING_URL)
    teus_soup = BeautifulSoup(teus_response.text, 'html.parser')
    teus_links = teus_soup.find_all('a', href=True)
    for link in teus_links:
        href = link['href']
        if href.lower().endswith('.pdf') or 'rwcgi60.exe' in href:
            if not href.startswith('http'):
                file_url = 'https://kpt.gov.pk' + href if href.startswith('/') else href
            else:
                file_url = href
            file_name = f"{today_str}_teus-handling.pdf"
            file_path = os.path.join(today_folder, file_name)
            print(f"Downloading {file_url} to {file_path}")
            try:
                file_resp = requests.get(file_url)
                with open(file_path, 'wb') as f:
                    f.write(file_resp.content)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pytz
import openpyxl



# URLs to scrape
PAGES = [
    ("Expected Arrivals", "https://kpt.gov.pk/pages/48/shipping-intelligence"),
    ("Ships Off Port", "https://kpt.gov.pk/pages/52/ships-off-port"),
    ("Ship Departures", "https://kpt.gov.pk/pages/53/ship-departures"),
    ("Ship On Port", "https://kpt.gov.pk/pages/54/ship-on-port"),
]


# Database and Excel setup
DB_NAME = "shipping_intelligence.db"
# Use the same Pakistani timezone timestamp
today_str = pk_now.strftime('%Y-%m-%d_%H-%M-%S')
EXCEL_NAME = os.path.join(today_folder, "expected_arrival.xlsx")

def create_tables(conn):
    cur = conn.cursor()
    # Example: Table for expected arrivals (expand as needed for other sections)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expected_arrivals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            shipping_agent TEXT,
            arrival_strip TEXT,
            import_export TEXT,
            cargo TEXT,
            last_updated TEXT
        )
    ''')
    # Add more tables for other sections as needed
    conn.commit()


def scrape_and_store():
    conn = sqlite3.connect(DB_NAME)
    create_tables(conn)
    cur = conn.cursor()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet

    for page_name, page_url in PAGES:
        print(f"Scraping {page_name}: {page_url}")
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        ws = wb.create_sheet(title=page_name[:31])  # Excel sheet name max 31 chars

        # Extract the 'Updated on' date from the <h4> tag
        updated_on = ""
        h4_tag = soup.find('h4', string=lambda t: t and 'Updated on' in t)
        if h4_tag:
            updated_on = h4_tag.get_text(strip=True)
            ws.append([updated_on])
            ws.append([])  # Blank row for separation

        last_updated = pk_now.strftime('%Y-%m-%d %H:%M:%S %Z')

        tables = soup.find_all('table', class_='ContainerGrid')
        for table in tables:
            rows = table.find_all('tr')
            section = None
            headers = []
            for i, row in enumerate(rows):
                ths = row.find_all('th')
                tds = row.find_all('td')
                # Section header row
                if ths and len(ths) == 1 and ths[0].has_attr('colspan'):
                    section = ths[0].get_text(strip=True)
                    ws.append([])  # Blank row for separation
                    ws.append([section])
                    continue
                # Column header row
                if ths and len(ths) > 1:
                    headers = [th.get_text(strip=True) for th in ths]
                    ws.append(headers + ["Last Updated"])
                    continue
                # Data row
                if tds and headers:
                    cols = [td.get_text(strip=True) for td in tds]
                    ws.append(cols + [last_updated])

    wb.save(EXCEL_NAME)
    print(f"Excel file '{EXCEL_NAME}' saved with all specified pages.")
    conn.close()

if __name__ == "__main__":
    scrape_and_store()
    download_pdfs_and_convert()
