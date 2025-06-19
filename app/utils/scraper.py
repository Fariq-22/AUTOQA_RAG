import os
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
from typing import List,Dict
from config import FIRE_CRAWL_API
load_dotenv()

web_scraper = FirecrawlApp(api_key=FIRE_CRAWL_API)

async def crawl_website(root_url, limit=2):
    print(f"Starting crawl of {root_url}")
    try:
        result = web_scraper.crawl_url(root_url, limit=limit, scrape_options=ScrapeOptions(formats=['markdown']))
        return result.data
    except Exception as e:
        return e
    

async def get_crawled_urls(docs: List[object]) -> List[str]:
    """
    Extracts all crawled URLs from the metadata of FirecrawlDocument objects.
    """
    urls = []
    for doc in docs:
        meta = getattr(doc, "metadata", {}) or {}
        url = meta.get("sourceURL") or meta.get("url")
        if url:
            urls.append(url)
    return urls



async def scrape_multiple_urls(urls: List[str],formats: List[str] = ["markdown"],timeout_ms: int = 120_000) ->List[Dict]:

    batch_result = web_scraper.batch_scrape_urls(
        urls,
        formats=formats,
        timeout=timeout_ms
    )
    
    return batch_result.data
