from routers.create_collection import router as knowledge_router
from fastapi import FastAPI

app=FastAPI()
app.include_router(knowledge_router, prefix="/Rag")
