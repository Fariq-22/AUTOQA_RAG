# app/main.py
from fastapi import FastAPI
from api.routers.create_collection import router as kb_router
from api.routers.database_information import router as db_router
from api.routers.retrival_router import router as retrival_router

app = FastAPI(
    title="KAPTURECX RAG Service",
    version="1.0.0",
    description="The services is used to create the knowledge Base. "
)

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
