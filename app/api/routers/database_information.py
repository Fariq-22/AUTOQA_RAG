from fastapi import APIRouter,HTTPException
from utils.db_query import list_all_collection,delete_collection
from pydantic import BaseModel,Field
from services.mongodb_client import get_mongodb_connection

router = APIRouter()



class Delete_Collection(BaseModel):
    coll_name:str = Field(...,description="provide collection name to delete")


class StatusRequest(BaseModel):
    cmd_id: str = Field(..., description="Client-specific unique ID")
    name: str = Field(..., description="The name of the knowledge base")




@router.post("/list_collection",summary="The endpoint is used to list all the collections inside the database",
    description="""
   The Endpoint is used to list all the collections in an database
    """)
async def list_collections():
    try:
        coll = await list_all_collection()
        return {"Collection":coll}
    except Exception as e:
        return {"error":str(e)}
    




@router.delete("/delete_collection", summary="Delete a collection")
async def delete_collec(payload: Delete_Collection):
    try:
        ok = await delete_collection(
            collection_name=payload.coll_name,
        )
        if ok:
            return {"message": f"Collection '{payload.coll_name}' in database "
                    }
        else:
            return {
                "message": "Collection deletion reported failure",
                "collection": payload.coll_name,
            }
    except Exception as e:
        return {"error": str(e)}



@router.post("/collection_status", summary="Check the status of the knowledge base ingestion")
async def retrieve_collection_status(payload: StatusRequest):
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

    # Extract status and optionally error details
    status = document.get("status", "Unknown")
    error = document.get("error")

    # Structure a user-friendly response
    response = {"status": status}
    if error:
        response["error"] = error

    return response



