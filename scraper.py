from playwright.sync_api import sync_playwright
import pandas as pd
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def scrape_google_maps(page, business_type, location):
    data = []
    query = f"{business_type.replace(' ', '+')}+in+{location.replace(' ', '+')}"
    page.goto(f"https://www.google.com/maps/search/{query}", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    listings = page.locator('a.hfpxzc').all()
    for listing in listings[:5]: # Limit kam kar di
        try:
            listing.click()
            page.wait_for_timeout(2000)
            name = page.locator('h1.DUwDvf').first.text_content() if page.locator('h1.DUwDvf').count() > 0 else "N/A"
            data.append({"Business Name": name, "Source": "Google Maps"})
        except: continue
    return data

def run_lead_scraper(business_type, location):
    all_data = []
    with sync_playwright() as p:
        # Ek hi browser launch hoga pure process mein
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--single-process"])
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        
        # Resources block karna (Images/Fonts block karne se RAM bachti hai)
        page.route("**/*.{png,jpg,jpeg,gif,css,font}", lambda route: route.abort())

        all_data.extend(scrape_google_maps(page, business_type, location))
        # Yahan baqi functions (Yellowpages/Yelp) bhi isi 'page' object ko use kar sakte hain
        
        browser.close()
    return pd.DataFrame(all_data)
