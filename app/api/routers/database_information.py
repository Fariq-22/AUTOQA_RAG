from fastapi import APIRouter
from utils.db_query import list_all_databases,drop_database_end,list_all_collection,cre_database,delete_collection
from pydantic import BaseModel,Field


router = APIRouter()


class Delete(BaseModel):
    dbname:str = Field(...,description="Provide the Database_Name to Delete")

class Delete_Collection(BaseModel):
    dbname:str = Field(...,description="Provide the Database name")
    coll_name:str = Field(...,description="")



@router.post("/create_database",summary="The endpoint is used to create the endpoint"
             ,description="The endpoint used to create the database")
async def create_db(payload:Delete):
    try:
        result = await cre_database(payload.dbname)
        if result==True:
            return {f"The database is created {payload.dbname}"}
        else:
            return {f"The database is not created"}
    except Exception as e:
        return {"error":str(e)}



@router.post("/get_db_list", summary="To list the database",
    description="""
   It will list all the database available
   
    """)
async def list_database():
    databases = await list_all_databases()
    return {"Available_databases":databases}
    
   



@router.post("/list_collection",summary="The endpoint is used to list all the collections inside the database",
    description="""
   The Endpoint is used to list all the collections in an database
    """)
async def list_collections(payload:Delete):
    try:
        coll = await list_all_collection(payload.dbname)
        return {"Collection":coll}
    except Exception as e:
        return {"error":str(e)}
    


@router.delete("/delete_database",summary="The endpoint is used to delete the database",
    description="""
   All the collection should be deleted to drop the database
   Use the list_collection_with_db end to check the db is empty or having collection
    """)
async def delete_database(payload:Delete):
    try:
        result=await drop_database_end(payload.dbname)
        if result == True:
            return {f"{payload.dbname} is deleted"}
    except Exception as e:
        return {"error":str(e)}



@router.delete("/delete_collection", summary="Delete a collection")
async def delete_collec(payload: Delete_Collection):
    try:
        ok = await delete_collection(
            dbname=payload.dbname,
            collection_name=payload.coll_name,
        )
        if ok:
            return {"message": f"Collection '{payload.coll_name}' in database "
                               f"'{payload.dbname}' was deleted."}
        else:
            return {
                "message": "Collection deletion reported failure",
                "database": payload.dbname,
                "collection": payload.coll_name,
            }
    except Exception as e:
        return {"error": str(e)}

