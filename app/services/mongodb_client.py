import os
import logging
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI,MONGODB_NAME
from uuid import uuid4
from datetime import datetime

# Global references to the client & DB
mongo_client = None
mongo_db = None

def get_mongodb_connection():
    """
    Returns an async Motor client and db instance.
    """
    global mongo_client, mongo_db

    if mongo_client and mongo_db is not None:
        return mongo_client, mongo_db

    try:
        mongo_client = AsyncIOMotorClient(MONGODB_URI)
        mongo_db = mongo_client[MONGODB_NAME]
        logging.info("Async MongoDB connection established successfully.")
        return mongo_client, mongo_db
    except Exception as e:
        logging.critical(f"Error establishing MongoDB connection: {e}")
        mongo_client, mongo_db = None, None
        return mongo_client, mongo_db


# async def dump_knowledge_base_info(cmd_id,name,link,know_base_id,error=None):
#     _, db = get_mongodb_connection()
#     document={
#         "_id" : str(uuid.uuid4()) + str(datetime.datetime.now().timestamp()),
#         "cm_id":cmd_id,
#         "name":name,
#         "link":link,
#         "status":"Processing",
#         "know_base_id":know_base_id,
#         "added_at": datetime.datetime.now().isoformat(),
#         "updated_at":None,
#         "error": error
#         }
#     await db["Web_Info"].insert_one(document)


# async def update_dump_knowledge_base_info(cmd_id,name,link,know_base_id,error=None):
#     _, db = get_mongodb_connection()
#     document={
#         "_id" : str(uuid.uuid4()) + str(datetime.datetime.now().timestamp()),
#         "cm_id":cmd_id,
#         "name":name,
#         "link":link,
#         "status":"Completed",
#         "know_base_id":know_base_id,
#         "added_at": datetime.datetime.now().isoformat(),
#         "updated_at":None,
#         "error": error
#         }
#     await db["Web_Info"].insert_one(document)



async def dump_or_update_knowledge_info(cmd_id, name, link, know_base_id, crawl_websites,status, error=None):
    _, db = get_mongodb_connection()
    now = datetime.now().isoformat()

    # Upsert by knowledge_base_id (assumes it's unique)
    await db["Web_Info"].update_one(
        {"know_base_id": know_base_id},
        {
            "$set": {
                "cm_id": cmd_id,
                "name": name,
                "link": link,
                "status": status,
                "crawl_websites_links":crawl_websites,
                "updated_at": now,
                "error": error,
            },
            "$setOnInsert": {
                "_id": str(uuid4()) + str(datetime.now().timestamp()),
                "added_at": now,
                "know_base_id": know_base_id,
            },
        },
        upsert=True
    )
