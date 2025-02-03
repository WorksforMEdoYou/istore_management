from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Stock
import logging
from sqlalchemy.orm import Session
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster, StoreDetails
from bson import ObjectId
from datetime import datetime
from ..utils import validate_by_id
from ..crud.stock import create_stock_collection_db, get_all_stocks_by_store_db, get_stock_collection_by_id_db, delete_stock_collection_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_stock_collection(stock: Stock, db, mysql_db:Session):
    """
    Creating the stock collection in the database.
    """
    try:
        stock_dict = stock.dict(by_alias=True)
        
        #validate_store_id
        if validate_by_id(id=stock_dict["store_id"], model=StoreDetails, field="store_id", db=mysql_db) == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        #validate_medicine_id
        if validate_by_id(id=stock_dict["medicine_id"], model=MedicineMaster, field="medicine_id", db=mysql_db) == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        stocks = {
            "store_id": stock_dict["store_id"],
            "medicine_id": stock_dict["medicine_id"],
            "medicine_form": stock_dict["medicine_form"],
            "available_stock": stock_dict["available_stock"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active_flag": 1,            
            "batch_details": [
                {
                    "expiry_date": item["expiry_date"],
                    "units_in_pack": item["units_in_pack"],
                    "batch_quantity": item["batch_quantity"],
                    "batch_number": item["batch_number"]
                }
                for item in stock_dict["batch_details"]
            ]
        }
        result = await create_stock_collection_db(stocks=stocks, db=db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_all_stocks_by_store(store_id: int, db, mysql_db:Session):
    """
    Get all stocks by store id.
    """
    try:
        result = await get_all_stocks_by_store_db(store_id=store_id, db=db, mysql_db=mysql_db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_stock_collection_by_id(store_id:int, medicine_id:int, db, mysql_db:Session):
    """
    Getting the stock collection by id from the database.
    """
    try:
        stock = await get_stock_collection_by_id_db(store_id=store_id, medicine_id=medicine_id, db=db, mysql_db=mysql_db)
        if stock:
            return stock
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_stock_collection(store_id:int, medicine_id:int, db=Depends(get_database)):
    """
    Deleting the stock collection from the database.
    """
    try:
        delete_result = await delete_stock_collection_db(store_id=store_id, medicine_id=medicine_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))