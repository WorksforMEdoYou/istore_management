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

async def create_sale_collection_dal(new_sale_data_dal, db):
    """
    Creating the sale collection in the database.
    """
    try:
        await db["sales"].insert_one(new_sale_data_dal)
        return new_sale_data_dal
    except Exception as e:
        logger.error(f"Database error while creating a sale DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating a sale DAL: " + str(e))
    
async def get_sales_list_dal(store_id: int, db):
    try:
        sales_list = []
        async for sale in db.sales.find({"store_id": store_id, "active_flag":1}):
            sale["_id"] = str(sale["_id"])
            sales_list.append(sale)
        
        return sales_list
    except Exception as e:
        logger.error(f"Database error in listing the sales DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in listing the sales DAL: " + str(e))

async def get_sale_particular_dal(sale_id: str, db):
    """
    Get sale particular
    """
    try:
        particular_sale = await db["sales"].find_one({"_id": ObjectId(sale_id)})
        if particular_sale:
            particular_sale["_id"] = str(particular_sale["_id"])
            return particular_sale
        raise HTTPException(status_code=404, detail="Sale not found")
    except Exception as e:
        logger.error(f"Database error in fetching particular sale DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching particular sale DAL: " + str(e))

async def delete_sale_collection_dal(sale_id: str, db):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_sale = await db.sales.update_one({"_id": ObjectId(sale_id)}, {"$set": {"active_flag": 0}})
        if delete_sale.modified_count == 1:
            return delete_sale
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error while deleting the sale DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while deleting the sale DAL: " + str(e))