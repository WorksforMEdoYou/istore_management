from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from ..crud.sales import create_sale_collection_db, get_sale_particular_db, read_sales_db, delete_sale_collection_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_sale_collection(sale: Sale, db):
    """
    Creating the sale collection in the database.
    """
    try:
        result = await create_sale_collection_db(sale=sale, db=db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sales(store_id:int, db):
    """
    Get the sale
    """
    try:
        sales = await read_sales_db(store_id=store_id, db=db)
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sale_particular(sale_id: str, db):
    """
    Get the sale particular
    """
    try:
        sale = await get_sale_particular_db(sale_id=sale_id, db=db)
        return sale
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_sale_collection(sale_id: str, db):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_result = await delete_sale_collection_db(sale_id=sale_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
