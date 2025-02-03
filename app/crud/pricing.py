from fastapi import Depends, HTTPException
from typing import List
from datetime import datetime
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
from ..schemas.Pricing import UpdatePricing
import logging
from bson import ObjectId
from ..utils import discount

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_pricing_collection_db(pricing, db):
    """
    Creating the pricing collection in the database.
    """
    try:
        result = await db.pricing.insert_one(pricing)
        pricing["_id"] = str(result.inserted_id)
        return pricing
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_all_collection_db(store_id: int, medicine_id: int, db):
    """
    Fetching all the data from the pricing collection in the database.
    """
    try:
        result = await db.pricing.find({"store_id": store_id, "medicine_id": medicine_id, "active_flag": 1}).to_list(length=None)
        for item in result:
            item["_id"] = str(item["_id"])
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_pricing_collection_db(store_id: int, medicine_id: int, db):
    """
    Deleting the pricing collection in the database.
    """
    try:
        result = await db.pricing.update_one({"store_id": store_id, "medicine_id": medicine_id}, {"$set": {"active_flag": 0}})
        if result.modified_count == 1:
            return {"message": "Pricing deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))