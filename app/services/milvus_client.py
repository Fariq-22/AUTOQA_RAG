from pymilvus import MilvusClient

from config import (
    MILVUS_URI, MILVUS_TOKEN
)




async def get_milvus_client(uri: str = MILVUS_URI, token: str = MILVUS_TOKEN, db_name: str = None) -> MilvusClient:
    """
    Returns a MilvusClient instance.
    
    If db_name is provided, connects to that database.
    If not, connects using default database.
    """
    try:
        if db_name:
            return MilvusClient(uri=uri, token=token, db_name=db_name)
        return MilvusClient(uri=uri, token=token)
    except Exception as e:
        print(f"Failed to connect to Milvus (db_name={db_name}): {e}")
        raise