import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
import pandas as pd
import random

# --- Google Sheet Connection Setup ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
# 'credentials.json' wahi file hai jo aapne Google Cloud se download ki thi
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
# 'LeadData' apni Google Sheet ka naam yahan likhein
sheet = client.open("LeadData").sheet1

def save_to_sheet(df):
    """Data ko saaf karke Google Sheet mein upload karta hai."""
    sheet.clear()  # Purana data saaf karein
    sheet.append_row(df.columns.tolist())  # Headers likhein
    sheet.append_rows(df.values.tolist())  # Data upload karein
    print("✅ Data successfully updated in Google Sheet!")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

def scrape_google_maps(business_type, location):
    data = []
    print(f"🔍 Searching for {business_type} in {location}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_context(user_agent=random.choice(USER_AGENTS)).new_page()
        query = f"{business_type.replace(' ', '+')}+in+{location.replace(' ', '+')}"
        page.goto(f"https://www.google.com/maps/search/{query}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        
        container = page.locator('div[role="feed"]')
        if container.count() > 0:
            container.evaluate("node => node.scrollTop += 3000")
            page.wait_for_timeout(3000)
        
        listings = page.locator('a.hfpxzc').all()
        for listing in listings[:8]:
            try:
                listing.click()
                page.wait_for_timeout(3000)
                name = page.locator('h1.DUwDvf').first.text_content() if page.locator('h1.DUwDvf').count() > 0 else "N/A"
                phone = page.locator('button[data-tooltip="Copy phone number"]').first.get_attribute('aria-label') if page.locator('button[data-tooltip="Copy phone number"]').count() > 0 else "N/A"
                address = page.locator('button[data-item-id="address"]').first.get_attribute('aria-label') if page.locator('button[data-item-id="address"]').count() > 0 else "N/A"
                website = page.locator('a[data-item-id="authority"]').first.get_attribute('href') if page.locator('a[data-item-id="authority"]').count() > 0 else "N/A"
                data.append({"Business Name": name, "Phone": phone.replace("Phone: ", ""), "Address": address.replace("Address: ", ""), "Website": website, "Source": "Google Maps"})
            except: continue
        browser.close()
    return pd.DataFrame(data)

def run_lead_scraper(business_type, location):
    """Scraper run karke seedha Google Sheet mein bhejta hai."""
    df = scrape_google_maps(business_type, location)
    if not df.empty:
        save_to_sheet(df)
    else:
        print("⚠️ No data found.")
    return df

# Test karne ke liye (Niche wali lines run karne par chalti hain)
if __name__ == "__main__":
    run_lead_scraper("Plumbers", "New York")
