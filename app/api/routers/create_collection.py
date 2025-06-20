from fastapi import APIRouter,HTTPException
from pydantic import BaseModel, Field
from typing import List

from utils.scraper import crawl_website,get_crawled_urls,scrape_multiple_urls
from utils.extracted import extract_pages_to_json, all_content_formatting ,download_extract_text_from_pdf
from utils.chunking import Recursive_chunking
from services.collection_schema import Create_Collection
from utils.db_query import insert_data_to_collection
import logging
from services.mongodb_client import dump_or_update_knowledge_info,get_mongodb_connection
from utils.unique_id import generate_safe_collection_name

router = APIRouter()

class LinkToKnowledge(BaseModel):
    name: str = Field(..., description="The database name to create the knowledge")
    cmd_id: str = Field(..., description="The Collection name of the Database")
    link: str = Field(..., description="The link for web scraping")


class Weblink(BaseModel):
    cmd_id: str = Field(..., description="Client-specific unique ID")
    name: str = Field(..., description="The name of the knowledge base")




class Multiple_Links(BaseModel):
    name: str = Field(..., description="The database name to create the knowledge")
    cmd_id: str = Field(..., description="The Collection name of the Database")
    multi_links: List[str] = Field(..., description="The link for web scraping")


@router.post("/web_link_to_knowledge", summary="Create a knowledge base from a web link",description="""
        Crawls the provided web link, scrapes content, and stores it in Milvus.

        - `name`: The name of the knowldeg 
        - `cmd_id`: unique cmd id for each client
        - `link`: The link to crawl/scrape
             """)
async def Making_Knowledge_Base(payload: LinkToKnowledge):
    knowledge_base_id = generate_safe_collection_name(payload.cmd_id)

    # Initially mark as processing
    await dump_or_update_knowledge_info(
        cmd_id=payload.cmd_id,
        name=payload.name,
        link=payload.link,
        know_base_id=knowledge_base_id,
        crawl_websites=None,
        status="Processing"
    )

    try:
        web_scraping_data = await crawl_website(payload.link)
        print("<<<<<--- Web Scraping Completed ---->>>>>>>>")
        links= await get_crawled_urls(web_scraping_data)

        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.link,
            know_base_id=knowledge_base_id,
            crawl_websites=links,
            status="Web_scarped"
                    )
        extracted_json = await extract_pages_to_json(web_scraping_data)
        print("<<<<<--- Text formatted Completed ---->>>>>>>>")

        text = await all_content_formatting(extracted_json)
        chunked_text = await Recursive_chunking(text=text)
        print("<<<<<--- Chunking Completed ---->>>>>>>>")

        collection_ready = await Create_Collection(
            collection_name=knowledge_base_id,
            description=f"Web data for {payload.link}"
        )

        if not collection_ready:
            raise Exception("Failed to create or access collection")

        inserted = await insert_data_to_collection(
            collection_name=knowledge_base_id,
            chunked_data=chunked_text
        )

        if not inserted:
            raise Exception("Failed to insert data into Milvus collection")

        # Mark as completed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.link,
            know_base_id=knowledge_base_id,
            crawl_websites=links,
            status="Completed"
        )

        print("<<<<<--- Data Inserted Completed ---->>>>>>>>")

        return {
            "message": "Ingestion complete",
            "chunks_stored": len(chunked_text),
            "collection": knowledge_base_id,
            "database": "kapture"
        }

    except Exception as e:
        logging.exception("Failed during ingestion")

        # Mark as failed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.link,
            know_base_id=knowledge_base_id,
            crawl_websites=None,
            status="Failed",
            error=str(e)
        )

        return {"error": str(e)}




@router.post("/Multiple_web_link_to_knowledge", summary="Create a knowledge base from a multiple web link",description="""
        Crawls the provided web link, scrapes content, and stores it in Milvus.

        - `name`: str=The name of the knowldeg 
        - `cmd_id`:str= unique cmd id for each client
        - `link`: List=Need multiple link in an list
             """)
async def Making_Knowledge_Base_Multi_Links(payload: Multiple_Links):
    knowledge_base_id = generate_safe_collection_name(payload.cmd_id)

    # Initially mark as processing
    await dump_or_update_knowledge_info(
        cmd_id=payload.cmd_id,
        name=payload.name,
        link=payload.multi_links,
        know_base_id=knowledge_base_id,
        crawl_websites=None,
        status="Processing"
    )

    try:
        web_scraping_data = await scrape_multiple_urls(payload.multi_links)
        print("<<<<<--- Web Scraping Completed ---->>>>>>>>")
        links= await get_crawled_urls(web_scraping_data)

        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.multi_links,
            know_base_id=knowledge_base_id,
            crawl_websites=links,
            status="Web_scarped"
                    )
        extracted_json = await extract_pages_to_json(web_scraping_data)
        print("<<<<<--- Text formatted Completed ---->>>>>>>>")

        text = await all_content_formatting(extracted_json)
        chunked_text = await Recursive_chunking(text=text)
        print("<<<<<--- Chunking Completed ---->>>>>>>>")

        collection_ready = await Create_Collection(
            collection_name=knowledge_base_id,
            description=f"Web data for {payload.multi_links}"
        )

        if not collection_ready:
            raise Exception("Failed to create or access collection")

        inserted = await insert_data_to_collection(
            collection_name=knowledge_base_id,
            chunked_data=chunked_text
        )

        if not inserted:
            raise Exception("Failed to insert data into Milvus collection")

        # Mark as completed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.multi_links,
            know_base_id=knowledge_base_id,
            crawl_websites=links,
            status="Completed"
        )

        print("<<<<<--- Data Inserted Completed ---->>>>>>>>")

        return {
            "message": "Ingestion complete",
            "chunks_stored": len(chunked_text),
            "collection": knowledge_base_id,
            "database": "kapture"
        }

    except Exception as e:
        logging.exception("Failed during ingestion")

        # Mark as failed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.multi_links,
            know_base_id=knowledge_base_id,
            crawl_websites=links,
            status="Failed",
            error=str(e)
        )

        return {"error": str(e)}


@router.post("/PDF_link_to_knowledge", summary="Create a knowledge base from a multiple PDF Files",description="""
        scarpe the data from pdf , and stores it in Milvus.

        - `name`: str=The name of the knowldeg 
        - `cmd_id`:str= unique cmd id for each client
        - `link`: List=links of the pdf
             """)
async def Making_Knowledge_Base_PDF(payload: Multiple_Links):
    knowledge_base_id = generate_safe_collection_name(payload.cmd_id)

    # Initially mark as processing
    await dump_or_update_knowledge_info(
        cmd_id=payload.cmd_id,
        name=payload.name,
        link=payload.multi_links,
        know_base_id=knowledge_base_id,
        crawl_websites=None,
        status="Processing"
    )

    try:
        pdf_content = await download_extract_text_from_pdf(payload.multi_links)
        print("<<<<<--- PDF Scarping Completed ---->>>>>>>>")

        chunked_text = await Recursive_chunking(text=pdf_content)
        print("<<<<<--- Chunking Completed ---->>>>>>>>")

        collection_ready = await Create_Collection(
            collection_name=knowledge_base_id,
            description=f"PDF data for {payload.multi_links}"
        )

        if not collection_ready:
            raise Exception("Failed to create or access collection")

        inserted = await insert_data_to_collection(
            collection_name=knowledge_base_id,
            chunked_data=chunked_text
        )

        if not inserted:
            raise Exception("Failed to insert data into Milvus collection")

        # Mark as completed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.multi_links,
            know_base_id=knowledge_base_id,
            crawl_websites=None,
            status="Completed"
        )

        print("<<<<<--- Data Inserted Completed ---->>>>>>>>")

        return {
            "message": "Ingestion complete",
            "chunks_stored": len(chunked_text),
            "collection": knowledge_base_id,
            "database": "kapture"
        }

    except Exception as e:
        logging.exception("Failed during ingestion")

        # Mark as failed
        await dump_or_update_knowledge_info(
            cmd_id=payload.cmd_id,
            name=payload.name,
            link=payload.multi_links,
            know_base_id=knowledge_base_id,
            crawl_websites=None,
            status="Failed",
            error=str(e)
        )

        return {"error": str(e)}


@router.post("/Scarped_website_links", summary="Used to retrive the links from mogo")
async def retrieve_weblinks(payload: Weblink):
    # Get a connection to MongoDB
    _, db = get_mongodb_connection()

    # Try to find the document using cmd_id and name
    document = await db["Web_Info"].find_one({
        "cm_id": payload.cmd_id,
        "name": payload.name
    })

    # If document doesn't exist, raise a 404 error
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")

    # Extract website_links and optionally error details
    scarped_links = document.get("crawl_websites_links", "Unknown")
    error = document.get("error")

    # Structure a user-friendly response
    response = {"scarped_links": scarped_links}
    if error:
        response["error"] = error

    return response