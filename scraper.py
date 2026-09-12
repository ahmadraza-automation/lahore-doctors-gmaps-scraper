import asyncio
from playwright.async_api import async_playwright
import csv

async def scrape_all_google_maps_doctors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        search_url = "https://www.google.com/maps/search/Doctors+in+Lahore"
        print(f"Opening URL: {search_url}")
        
        await page.goto(search_url, timeout=60000)
        await page.wait_for_timeout(5000)

        print("Scrolling results panel to load all doctors... (Ye thoda waqt le sakta hai)")
        
        # Infinite scroll jab tak mazeed results load hona band na ho jayein
        try:
            sidebar = page.locator('div[role="feed"]')
            last_count = 0
            while True:
                # Panel ko neechay scroll karein
                await sidebar.evaluate("node => node.scrollBy(0, 5000)")
                await page.wait_for_timeout(3000) # Naye cards load hone ka intezaar
                
                # Check karein ke mazeed listings aayi hain ya nahi
                listings = await page.locator('div.Nv2PK').all()
                current_count = len(listings)
                print(f"Loaded {current_count} listings so far...")
                
                if current_count == last_count:
                    print("All listings loaded!")
                    break
                last_count = current_count
                
                # Agar aapko limit lagani hai (misal ke taur par 200 doctors tak), toh yahan condition laga sakte hain
                if current_count >= 200: 
                    break
        except Exception as e:
            print("Scrolling note:", e)

        doctors_data = []
        listings = await page.locator('div.Nv2PK').all()
        print(f"Extracting details for {len(listings)} doctors...")

        for listing in listings:
            try:
                name_elem = listing.locator('.fontHeadlineSmall')
                name = await name_elem.inner_text() if await name_elem.count() > 0 else "N/A"

                text_content = await listing.inner_text()
                phone = "N/A"
                for line in text_content.split('\n'):
                    if any(char.isdigit() for char in line) and ('+' in line or '03' in line or '-' in line):
                        if len(line.strip()) > 9 and len(line.strip()) < 20:
                            phone = line.strip()
                            break

                doctors_data.append({
                    "Name": name.strip(),
                    "Phone/WhatsApp": phone,
                    "Source": "Google Maps Lahore"
                })
            except Exception as e:
                print(f"Error parsing listing: {e}")

        csv_file = "lahore_doctors_gmaps_all.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Phone/WhatsApp", "Source"])
            writer.writeheader()
            writer.writerows(doctors_data)

        print(f"Data successfully saved to {csv_file}")
        await browser.close()

asyncio.run(scrape_all_google_maps_doctors())
