from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import parse_obj_as
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Order
import logging
from datetime import datetime
from ..models.store_mysql_models import MedicineMaster
from ..utils import validate_by_id
from sqlalchemy.orm import Session
from ..crud.orders import create_order_collection_db, get_order_collection_db, get_order_collection_pending_db, get_order_collection_delivered_db, delete_order_collection_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_order_collection(order: Order, db=Depends(get_database)):
    """
    Create a new order in the database.
    """
    try:
        order_dict = order.dict(by_alias=True)
        result = {
            "store_id": order_dict["store_id"],
            "customer_id": order_dict["customer_id"],
            "order_date": order_dict["order_date"],
            "payment_method": order_dict["payment_method"],
            "total_amount": order_dict["total_amount"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active_flag": 1,
            "order_status": "pending",  # Default order status
            "order_items": order_dict["order_items"]
        }
        # Insert the order into the database
        orders = await create_order_collection_db(order=result, db=db)
        return orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_order_collection(store_id: int, db):
    """
    Get a specific order from the database.
    """
    try:
        order = await get_order_collection_db(store_id=store_id, db=db)
        return order
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_order_collection_delivered(store_id: int, db):
    """
    Get a specific order from the database.
    """
    try:
        order = await get_order_collection_delivered_db(store_id=store_id, db=db)
        return order
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_order_collection_pending(store_id: int, db):
    """
    Get a specific order from the database.
    """
    try:
        order = await get_order_collection_pending_db(store_id=store_id, db=db)
        return order
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


async def delete_order_collection(order_id: str, db=Depends(get_database)):
    """
    Delete a specific order from the database.
    """
    try:
        delete_result = await delete_order_collection_db(order_id=order_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))