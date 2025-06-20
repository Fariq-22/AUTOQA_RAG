from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from typing import Dict

from services.retrival import vector_search
from services.retrival import keyword_search,fetch_all_docs
from services.retrival import hybrid_retrieve

from services.llm_services import RAG_Answering,generate_subqueries

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
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/keyword_search",summary="To retrive the documents from given collection via keyword search",
             description="It retrive most relavent docs")
async def keyword_retrival(payload:Retrival):
    try:
        texts, tokens = await fetch_all_docs(collection=payload.coll)
        kw = await keyword_search(payload.query, texts, tokens)
        return kw
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid_search",summary="To retrive the documents from given collection via keyword + vector search",
             description="It retrive most relavent docs")
async def hybrid_retrival(payload:Retrival)-> Dict:
    try:
        hybrid_ret = await hybrid_retrieve(collection_name=payload.coll,query=payload.query)
        print(hybrid_ret)
        retrived_info = f"Question:{payload.query} Retrived_data:{hybrid_ret}"
        print("____________________________________________________________")
        print(retrived_info)
        response_from_rag= await RAG_Answering(retrived_information=retrived_info)
        return {"status_code":200,"response":response_from_rag}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/Multi_hybrid_search",summary="To retrive the documents from given collection via keyword + vector search of multiple query's generated from llmn",
             description="It retrive most relavent docs")
async def multi_hybrid_search(payload:Retrival) -> Dict:
    try:
        subqueries = await generate_subqueries(payload.query)
        all_chunks = []
        retrieval_map = {}
        for subq in subqueries:
            chunks = await hybrid_retrieve(collection_name=payload.coll,query= subq,top_k=2)
            retrieval_map[subq] = chunks
        all_chunks.extend(chunks)
        print(all_chunks)
        # Prepare RAG input
        rag_input = f"Question: {payload.query},Retrieved:{retrieval_map}"
        rag_response = await RAG_Answering(retrived_information=rag_input)
        # return {"subqueries": subqueries, "retrievals": retrieval_map, "rag": rag_response}
        return {"status_code":200,"response":rag_response}
        # return rag_input
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


