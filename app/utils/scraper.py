import os
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
from config import FIRE_CRAWL_API
load_dotenv()

web_scraper = FirecrawlApp(api_key=FIRE_CRAWL_API)

async def crawl_website(root_url, limit=5):
    print(f"Starting crawl of {root_url}")
    result = web_scraper.crawl_url(root_url, limit=limit, scrape_options=ScrapeOptions(formats=['markdown']))
    return result.data