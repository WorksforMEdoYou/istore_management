from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_sale_collection_db(sale, db):
    """
    Creating the sale collection in the database.
    """
    try:
        await db["sales"].insert_one(sale)
        return sale
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def read_sales_db(store_id: int, db):
    try:
        sales = []
        async for sale in db.sales.find({"store_id": store_id, "active_flag":1}):
            sale["_id"] = str(sale["_id"])
            sales.append(sale)
        
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sale_particular_db(sale_id: str, db):
    """
    Get sale particular
    """
    try:
        result = await db["sales"].find_one({"_id": ObjectId(sale_id)})
        if result:
            result["_id"] = str(result["_id"])
            return result
        raise HTTPException(status_code=404, detail="Sale not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_sale_collection_db(sale_id: str, db):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_result = await db.sales.update_one({"_id": ObjectId(sale_id)}, {"$set": {"active_flag": 0}})
        if delete_result.modified_count == 1:
            return {
                "sale_id": sale_id,
                "message": "Sale order deleted successfully"
            }
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))