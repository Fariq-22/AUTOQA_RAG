from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.scraper import crawl_website
from utils.extracted import extract_pages_to_json, all_content_formatting  # fixed typo: extracted → extractor

router = APIRouter()

class LinkToKnowledge(BaseModel):
    Database_name: str = Field(..., description="The database name to create the knowledge")
    Collection_name: str = Field(..., description="The Collection name of the Database")
    link: str = Field(..., description="The link for web scraping")

@router.post("/web_link_to_knowledge", summary="Create a knowledge base from a web link",
    description="""
    Crawls the provided web link, scrapes content, and stores it in Milvus.

    - `Database_name`: The name of the database
    - `Collection_name`: The name of the collection
    - `link`: The link to crawl/scrape
    """)
async def conversation(payload: LinkToKnowledge):
    web_scraping_data = await crawl_website(payload.link)
    extracted_json = await extract_pages_to_json(web_scraping_data)
    text = await all_content_formatting(extracted_json)
    return {"extracted_text": text}
