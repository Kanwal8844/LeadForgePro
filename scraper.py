from playwright.sync_api import sync_playwright
import pandas as pd
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

def scrape_google_maps(business_type, location):
    data = []
    with sync_playwright() as p:
        # headless=False kr diya hai taake bot detection kam ho
        browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        
        query = f"{business_type} in {location}"
        page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
        
        page.wait_for_timeout(7000) # Thoda zyada wait taake page load ho
        
        # Feed scroll karna
        container = page.locator('div[role="feed"]')
        container.evaluate("node => node.scrollTop += 5000")
        page.wait_for_timeout(3000)

        listings = page.locator('a.hfpxzc').all()
        for listing in listings[:10]:
            try:
                listing.click()
                page.wait_for_timeout(4000)
                
                name = page.locator('h1.DUwDvf').first.text_content() if page.locator('h1.DUwDvf').count() > 0 else "N/A"
                
                # Phone, Address, Website selectors
                phone = page.locator('button[data-tooltip="Copy phone number"]').first.get_attribute('aria-label').replace("Phone: ", "") if page.locator('button[data-tooltip="Copy phone number"]').count() > 0 else "N/A"
                address = page.locator('button[data-item-id="address"]').first.get_attribute('aria-label').replace("Address: ", "") if page.locator('button[data-item-id="address"]').count() > 0 else "N/A"
                website = page.locator('a[data-item-id="authority"]').first.get_attribute('href') if page.locator('a[data-item-id="authority"]').count() > 0 else "N/A"
                
                data.append({"Business Name": name, "Phone": phone, "Address": address, "Website": website, "Source": "Google Maps"})
            except: 
                continue
        browser.close()
    return pd.DataFrame(data)

def scrape_yellow_pages(business_type, location):
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        page.goto(f"https://www.yellowpages.com/search?search_terms={business_type.replace(' ', '+')}&geo_location_terms={location.replace(' ', '+')}")
        
        cards = page.locator('div.result').all()
        for card in cards[:8]:
            try:
                name = card.locator('a.business-name span').text_content()
                phone = card.locator('div.phones').text_content() if card.locator('div.phones').count() > 0 else "N/A"
                address = card.locator('div.street-address').text_content() if card.locator('div.street-address').count() > 0 else "N/A"
                website = card.locator('a.track-visit-website').get_attribute('href') if card.locator('a.track-visit-website').count() > 0 else "N/A"
                data.append({"Business Name": name, "Phone": phone, "Address": address, "Website": website, "Source": "Yellow Pages"})
            except: continue
        browser.close()
    return pd.DataFrame(data)

def run_lead_scraper(business_type, location):
    # Filhal Google Maps ko call karein
    df1 = scrape_google_maps(business_type, location)
    df2 = scrape_yellow_pages(business_type, location)
    return pd.concat([df1, df2], ignore_index=True)
