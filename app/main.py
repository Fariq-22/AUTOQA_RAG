# app/main.py
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from api.routers.create_collection import router as kb_router
from api.routers.database_information import router as db_router
from api.routers.retrival_router import router as retrival_router

from config import milvus_client,DB_Name

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # On-startup logic
    if DB_Name not in milvus_client.list_databases():
        milvus_client.create_database(DB_Name)
        logger.info(f"Created Milvus database: {DB_Name}")
    else:
        logger.info(f"Milvus database already exists: {DB_Name}")
    yield  # Hand off to FastAPI


app = FastAPI(
        lifespan=lifespan,
    title="KAPTURECX RAG API",
    version="1.0.0",
    description="An automated Retrieval-Augmented Generation (RAG) pipeline that converts various sources—web URLs, PDFs, and static web pages—into a searchable knowledge base using Milvus."
)


@app.get("/_stcore/host-config",tags=["Status_Info"])
def host_config():
    return {"status": "ok"}


@app.get("/_stcore/health",tags=["Status_Info"])
def health():
    return {"status": "healthy"}



# All of your “web_link_to_knowledge” endpoints live here
app.include_router(
    kb_router,
    prefix="/Rag",
    tags=["Knowledge Base"],
)

# All of your database‐info endpoints live here
app.include_router(
    db_router,
    prefix="/Rag",
    tags=["Database Info"],
)


app.include_router(
    retrival_router,
    prefix="/Rag",
    tags=["Retrival options"],
)
