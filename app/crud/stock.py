from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Stock
import logging
from sqlalchemy.orm import Session
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster, Manufacturer, Category, Distributor, StoreDetails
from bson import ObjectId
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_stock_collection_dal(new_stocks_data_dal, db=Depends(get_database)):
    """
    Creating the stock collection in the database.
    """
    try:
        create_stock = await db.stocks.insert_one(new_stocks_data_dal)
        new_stocks_data_dal["_id"] = str(create_stock.inserted_id)
        logger.info(f"stock created with ID: {new_stocks_data_dal['_id']}")
        return new_stocks_data_dal
    except Exception as e:
        logger.error(f"Database error while creating the stock DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the stock DAL: " + str(e))

async def get_all_stocks_by_store_dal(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    """
    Get all stocks by store id.
    """
    try:
        stocks_list = db.stocks.find({"store_id": store_id})
        stocks = await stocks_list.to_list(length=None)
        if stocks:
            return stocks
    except Exception as e:
        logger.error(f"Database error while fetching the stocks list DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the stocks list DAL: " + str(e))

async def get_stock_collection_by_id_dal(store_id: int, medicine_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    """
    Getting the stock collection by id from the database.
    """
    try:
        stocks_list = db.stocks.find({"store_id": store_id, "medicine_id": medicine_id})
        purchases_list = db.purchases.find({"store_id": store_id, "purchase_items.medicine_id": medicine_id}).skip(0).limit(10)
        sales_list = db.sales.find({"store_id": store_id, "sale_items.medicine_id": medicine_id}).skip(0).limit(10)
        medicine_composition = mysql_db.query(MedicineMaster).filter(MedicineMaster.medicine_id == medicine_id).first()
        stocks_data = {
            "store_id": store_id,
            "medicine_id": medicine_id,
            "stocks": stocks_list,
            "purchases": purchases_list,
            "sales": sales_list,
            "medicine_composition": medicine_composition.composition if medicine_composition else None,
        }
        return stocks_data
    except Exception as e:
        logger.error(f"Database error while fetching the stock DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the stock DAL: " + str(e))

async def delete_stock_collection_dal(store_id:int, medicine_id:int, db):
    """
    Deleting the stock collection from the database.
    """
    try:
        delete_stock = await db.stocks.update_one({"store_id":store_id, "medicine_id":medicine_id}, {"$set": {"active_flag":0}})
        if delete_stock.modified_count == 1:
            return {"store_id": store_id, "medicine_id": medicine_id}
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error while deleting the stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while deleting the stock: " + str(e))