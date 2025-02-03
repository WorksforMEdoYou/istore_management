from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from sqlalchemy.orm import Session
from ..db.mysql_session import get_db
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Purchase
import logging
from ..crud.purchase import create_purchase_collection_db, delete_purchase_collection_db, get_all_purchases_db, get_purchases_by_id_db, get_purchases_by_date_db
from ..utils import validate_by_id
from ..models.store_mysql_models import MedicineMaster, Distributor, Manufacturer
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_purchase_collection(purchase: Purchase, db, mysql_db: Session):
    """
    Creating the purchase collection.
    """
    try:
        purchase_dict = purchase.model_dump(by_alias=True)
        purchase_collection = await create_purchase_collection_db(purchase=purchase_dict, db=db, mysql_db=mysql_db)
        return purchase_collection
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_all_purchase_list(store_id: int, db, mysql_db: Session):
    """
    Get all purchases
    """
    try:
        result = await get_all_purchases_db(store_id, db, mysql_db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_purchase_collection_by_id(purchase_id: str, db, mysql_db:Session):
    """
    Getting the purchase collection by id from the database.
    """
    try:
        purchase = await get_purchases_by_id_db(id=purchase_id, db=db, mysql_db=mysql_db)
        return purchase
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_purchases_by_date_store(store_id:int, db, mysql_db:Session, start_date:str=None, end_date:str=None):
    """
    Get all purchases by date and store
    """
    try:
        result = await get_purchases_by_date_db(store_id=store_id, db=db, mysql_db=mysql_db, start_date=start_date, end_date=end_date)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_purchase_collection(purchase_id: str, db=Depends(get_database)):
    
    """
    Deleting the purchase collection from the database.
    """
    try:
        delete_result = await delete_purchase_collection_db(purchase_id=purchase_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    