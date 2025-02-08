from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from sqlalchemy.orm import Session
from ..db.mongodb import get_database
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_purchase_collection_dal(new_purchse_data_dal, db):
    """
    Creating the purchase collection in the database.
    """
    try:
        create_pricing = await db.purchases.insert_one(new_purchse_data_dal)
        new_purchse_data_dal["_id"] = str(create_pricing.inserted_id)
        logger.info(f"Purchase created with ID: {new_purchse_data_dal['_id']}")
        return new_purchse_data_dal
    except Exception as e:
        logger.error(f"Database error while creating the purchase DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the purchase DAL: " + str(e))
    
async def get_all_purchases_list_dal(store_id: int, db):
    """
    Get all purchases from the database
    """
    try:
        purchases_list = db.purchases.find({"store_id": store_id, "active_flag": 1})
        if purchases_list:
            return purchases_list
    except Exception as e:
        logger.error(f"Database error while fetching the list of purchases DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the list of purchases DAL: " + str(e))

async def get_purchases_by_id_dal(id: str, db):
    """
    Get purchase by ID from the database
    """
    try:
        individual_purchase = await db.purchases.find_one({"_id": ObjectId(id)})
        if individual_purchase:
            return individual_purchase
    except Exception as e:
        logger.error(f"Database error while fetching the particular purchase DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the particular purchase DAL: " + str(e))

async def get_purchases_by_date_dal(store_id: int, db, start_date: str = None, end_date: str = None):
    """
    Get all purchases from the database store start_date and end_date
    """
    try:
        
        if start_date and end_date:
            # Parse the start and end dates
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Fetch purchases from MongoDB within the date range
            purchases_cursor = db.purchases.find({
                "store_id": store_id,
                "active_flag": 1,
                "purchase_date": {"$gte": start_date, "$lte": end_date}
            })
        else:
            # Fetch all purchases from MongoDB
            purchases_cursor = db.purchases.find({"store_id": store_id, "active_flag": 1})
        return purchases_cursor
    except Exception as e:
        logger.error(f"Database error in fetching the purchase by date range DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching the purchase by date range DAL: " + str(e))

async def delete_purchase_collection_dal(purchase_id: str, db=Depends(get_database)):
    
    """
    Deleting the purchase collection from the database.
    """
    try:
        delete_purchase = await db.purchases.update_one(
            {"_id": ObjectId(str(purchase_id))}, 
            {"$set": {"active_flag":0}})
        if delete_purchase.modified_count == 1:
            return delete_purchase
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error in deleting the purchase DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in deleting the purchase DAL: " + str(e))