from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.scraper import crawl_website
from utils.extracted import extract_pages_to_json, all_content_formatting 
from utils.chunking import Recursive_chunking
from services.milvus_client import get_milvus_client
from services.collection_schema import Create_Collection
from utils.db_query import insert_data_to_collection
import logging

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
    - [IMPORTANT] THE DATABASE_NAME AND COLLECTION_NAME SHOULD ONLY CONTAIN ALPHABETS AND NUMBERS NO SPECIAL SYMBOLS IS ALLOWED
    """)
async def Making_Knowledge_Base(payload: LinkToKnowledge):
    milvus_client = await get_milvus_client()
    web_scraping_data = await crawl_website(payload.link)
    print("<<<<<--- Web Scraping Completed ---->>>>>>>>")
    extracted_json = await extract_pages_to_json(web_scraping_data)
    print("<<<<<--- Text formated Completed ---->>>>>>>>")
    text = await all_content_formatting(extracted_json)
    chunked_text = await Recursive_chunking(text=text)
    print("<<<<<--- Chunked   Completed ---->>>>>>>>")

    if payload.Database_name not in milvus_client.list_databases():
        milvus_client.create_database(payload.Database_name)
        logging.info(f"The Database is created {payload.Database_name}")
    try:
        collection_ready = await Create_Collection(
            database_name=payload.Database_name,
            collection_name=payload.Collection_name,
            description=f"Web data for {payload.link}"
        )

        if not collection_ready:
            return {"error": "Failed to create or access collection"}
        
        inserted = await insert_data_to_collection(
            database_name=payload.Database_name,
            collection_name=payload.Collection_name,
            chunked_data=chunked_text
        )
        if not inserted:
            return {"error": "Failed to insert data into Milvus collection"}

        return {
            "message": "Ingestion complete",
            "chunks_stored": len(chunked_text),
            "collection": payload.Collection_name,
            "database": payload.Database_name
        }

    except Exception as e:
        logging.exception("Failed during ingestion")
        return {"error": str(e)}


