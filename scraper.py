from playwright.sync_api import sync_playwright
import pandas as pd
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def scrape_google_maps(business_type, location):
    data = []
    with sync_playwright() as p:
        # Render ke liye updated launch arguments
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

def scrape_yellow_pages(business_type, location):
    data = []
    with sync_playwright() as p:
        # Render ke liye updated launch arguments
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_context(user_agent=random.choice(USER_AGENTS)).new_page()
        page.goto(f"https://www.yellowpages.com/search?search_terms={business_type.replace(' ', '+')}&geo_location_terms={location.replace(' ', '+')}", wait_until="domcontentloaded", timeout=60000)
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

def scrape_yelp(business_type, location):
    data = []
    with sync_playwright() as p:
        # Render ke liye updated launch arguments
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        page.goto(f"https://www.yelp.com/search?find_desc={business_type.replace(' ', '+')}&find_loc={location.replace(' ', '+')}", wait_until="domcontentloaded", timeout=60000)
        
        listings = page.locator('div[data-testid="serp-iaim-card"]').all()
        
        for listing in listings[:5]:
            try:
                link_element = listing.locator('h3 a')
                business_url = "https://www.yelp.com" + link_element.get_attribute("href")
                
                new_page = context.new_page()
                new_page.goto(business_url, wait_until="domcontentloaded", timeout=60000)
                
                name = new_page.locator('h1').text_content() if new_page.locator('h1').count() > 0 else "N/A"
                phone = new_page.locator('p:has-text("+1")').first.text_content() if new_page.locator('p:has-text("+1")').count() > 0 else "N/A"
                address = new_page.locator('address').text_content() if new_page.locator('address').count() > 0 else "N/A"
                website = new_page.locator('a[rel="noopener"][target="_blank"]').first.get_attribute('href') if new_page.locator('a[rel="noopener"][target="_blank"]').count() > 0 else "N/A"
                
                data.append({"Business Name": name, "Phone": phone, "Address": address, "Website": website, "Source": "Yelp"})
                new_page.close()
            except: continue
        browser.close()
    return pd.DataFrame(data)

def run_lead_scraper(business_type, location):
    df1 = scrape_google_maps(business_type, location)
    df2 = scrape_yellow_pages(business_type, location)
    df3 = scrape_yelp(business_type, location)
    return pd.concat([df1, df2, df3], ignore_index=True)
