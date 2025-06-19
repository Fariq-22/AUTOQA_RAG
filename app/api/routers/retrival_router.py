from fastapi import APIRouter
from pydantic import BaseModel,Field

from services.retrival import vector_search
from services.retrival import keyword_search,fetch_all_docs
from services.retrival import hybrid_retrieve

from services.llm_services import RAG_Answering

router=APIRouter()

class Retrival(BaseModel):
    coll:str=Field(...,description="The name of the collection")
    query:str=Field(...,description="The User Query")

@router.post("/vector_search", summary="To retrive the data from particular collection via vector search",
    description="""
    It retrive the most relavent docments.
    """)
async def vector_retrival(paylod:Retrival):
    try:
        retrived_data = await vector_search(collection=paylod.coll,query=paylod.query)
        return retrived_data
    except Exception as e:
        return {"error":str(e)}



@router.post("/keyword_search",summary="To retrive the documents from given collection via keyword search",
             description="It retrive most relavent docs")
async def keyword_retrival(payload:Retrival):
    try:
        texts, tokens = await fetch_all_docs(collection=payload.coll)
        kw = await keyword_search(payload.query, texts, tokens)
        return kw
    except Exception as e:
        return {"error":str(e)}


@router.post("/hybrid_search",summary="To retrive the documents from given collection via keyword + vector search",
             description="It retrive most relavent docs")
async def hybrid_retrival(payload:Retrival):
    try:
        hybrid_ret = await hybrid_retrieve(collection_name=payload.coll,query=payload.query)
        retrived_info = {"Question":payload.query,"Retrived_data":hybrid_ret}
        # print(retrived_info)
        response_from_rag= await RAG_Answering(retrived_information=retrived_info)
        return response_from_rag
    except Exception as e:
        return {"error":str(e)}


