
from services.milvus_client import get_milvus_client
from utils.chunking import get_embeddings,bm25_tonized
from typing import List

async def insert_data_to_collection(database_name:str,collection_name:str,chunked_data:List)->bool:
    milvus_client= await get_milvus_client(db_name=database_name)
    tokenized_corpus=await bm25_tonized(chunked_data)
    embeddings=await get_embeddings(chunked_data)

    data = [
        {
            "embedding": embeddings[i],
            "text": chunked_data[i],
            "keyword_text":tokenized_corpus[i]
        }
        for i in range(len(chunked_data))
    ]

    result = milvus_client.insert(
    collection_name=collection_name,
    data=data)

    index_params = milvus_client.prepare_index_params()
    index_params.add_index(
    field_name="embedding",
    index_type="HNSW",
    metric_type="COSINE",
    params={
        "M": 16,
        "efConstruction": 200
    }
        )
    
    milvus_client.create_index(
    collection_name=collection_name,
    index_params=index_params
    )

    milvus_client.load_collection(collection_name=collection_name)

    if result['insert_count'] == len(chunked_data):
        return True
    else:
        return False
    

async def list_all_databases() -> List:
    """
    List all databases in the Milvus instance.
    """
    milvus_client= await get_milvus_client()
    return milvus_client.list_databases() 


async def drop_database_end(dbname:str) -> bool:
    milvus_client= await get_milvus_client()
    milvus_client.drop_database(dbname)

    if dbname not in milvus_client.list_databases():
        return True
    else:
        return False

async def list_all_collection(dbname:str) -> List:
    milvus_client= await get_milvus_client(db_name=dbname)
    li=milvus_client.list_collections()
    return li


async def delete_collection(dbname:str,collection_name:str) -> bool:
    milvus_client= await get_milvus_client(db_name=dbname)
    milvus_client.drop_collection(collection_name)

    if collection_name not in milvus_client.list_collections():
        return True
    else:
        return False
    

async def cre_database(dbname:str) -> bool:
    milvus_client= await get_milvus_client()
    milvus_client.create_database(dbname)

    if dbname in  milvus_client.list_databases():
        return True
    else:
        return False

    

