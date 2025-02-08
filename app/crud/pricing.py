from fastapi import Depends, HTTPException
from typing import List
from datetime import datetime
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
import logging
from bson import ObjectId
from ..utils import discount
from ..Service.pricing import UpdatePricing

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_pricing_collection_dal(new_pricing_dal, db):
    """
    Creating the pricing collection in the database.
    """
    try:
        create_pricing = await db.pricing.insert_one(new_pricing_dal)
        new_pricing_dal["_id"] = str(create_pricing.inserted_id)
        return new_pricing_dal
    except Exception as e:
        logger.error(f"Database error while creating the pricing DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the pricing DAL: " + str(e))

async def get_all_pricing_collection_dal(store_id: int, medicine_id: int, db):
    """
    Fetching all the data from the pricing collection in the database.
    """
    try:
        list_pricing = await db.pricing.find({"store_id": store_id, "medicine_id": medicine_id, "active_flag": 1}).to_list(length=None)
        for item in list_pricing:
            item["_id"] = str(item["_id"])
        return list_pricing
    except Exception as e:
        logger.error(f"Database error while fetching list of pricings DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching list of pricings DAL: " + str(e))

async def update_pricing_dal(pricing: UpdatePricing, pricing_discount, db):
    """
    Updating the pricing collection in the database.
    """
    try:
        update_pricing = await db.pricing.update_one(
            {"store_id": pricing.store_id, "medicine_id": pricing.medicine_id},
            {"$set": {"price": pricing_discount, "mrp": pricing.mrp, "discount": pricing.discount, "net_rate": pricing.net_rate, "updated_at":datetime.now()}}
        )
        if update_pricing.modified_count == 1:
            return update_pricing
        raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error while updating the pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating the pricing: " + str(e))
    
async def delete_pricing_collection_dal(store_id: int, medicine_id: int, db):
    """
    Deleting the pricing collection in the database.
    """
    try:
        delete_pricing = await db.pricing.update_one({"store_id": store_id, "medicine_id": medicine_id}, {"$set": {"active_flag": 0}})
        if delete_pricing.modified_count == 1:
            return delete_pricing
        else:
            raise HTTPException(status_code=404, detail="Pricing not found")
    except Exception as e:
        logger.error(f"Database error while deleting the pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while deleting the pricing: " + str(e))
    