# Lahore Doctors Google Maps Scraper

Playwright-based scraper to extract doctor listings (name + phone) from Google Maps search for "Doctors in Lahore".

## Requirements
- Python 3.8+
- playwright

```bash
pip install playwright
playwright install chromium
```

## Usage
```bash
python scraper.py
```

It will open a browser, scroll the results, extract data, and save to `lahore_doctors_gmaps_all.csv`.

**Note:** Scraped data is not included in this repository.
