from pymilvus import FieldSchema, DataType, CollectionSchema


import logging

from config import milvus_client

async def Create_Collection(
    collection_name: str,
    description: str = "The Knowledgebase for"
) -> bool:
    """
    Ensures `database_name` exists, then creates `collection_name` in it.
    Returns True if the collection exists afterwards (either pre‑existing or newly created).
    """


    if milvus_client.has_collection(collection_name):
        logging.info(f"[INFO] Collection '{collection_name}' already exists in DB kapture.")

    # 5) Define schema and create the collection
    try:
        fields = [
            FieldSchema(name="id",            dtype=DataType.INT64,        is_primary=True, auto_id=True),
            FieldSchema(name="embedding",     dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="text",          dtype=DataType.VARCHAR,      max_length=25_000),
            FieldSchema(
                name="keyword_text",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_capacity=750,
                max_length=712
            ),
        ]
        schema = CollectionSchema(
            fields,
            description=f"{description} '{collection_name}'",
            enable_dynamic_field=True
        )
        milvus_client.create_collection(collection_name, schema=schema)
    except Exception as e:
        logging.info(f"[ERROR] Failed to create collection: {e}")
        return False

    # 6) Verify creation
    exists = milvus_client.has_collection(collection_name)
    if exists:
        logging.info(f"[SUCCESS] Collection '{collection_name}' created in DB kapture.")
    else:
        logging.info(f"[ERROR] Collection '{collection_name}' not found after create call.")
    return exists



