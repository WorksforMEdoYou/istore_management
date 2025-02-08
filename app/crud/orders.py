from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import parse_obj_as
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Order
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_order_collection_dal(new_order_data_dal, db=Depends(get_database)):
    """
    Create a new order DAL.
    """
    try:
        create_order = await db.orders.insert_one(new_order_data_dal)
        new_order_data_dal["_id"] = str(create_order.inserted_id)
        logger.info(f"Order created with ID: {new_order_data_dal['_id']}")
        return new_order_data_dal
    except Exception as e:
        logger.error(f"Database error while creating orders DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating orders DAL: " + str(e))

async def get_order_collection_dal(store_id: int, db=Depends(get_database)):
    """
    Get a specific order from the database by store. 
    """
    try:
        orders_list = await db.orders.find_one({"store_id": store_id})
        if orders_list:
            return orders_list
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error while fetching orders list DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching orders list DAL: " + str(e))

async def get_order_collection_pending_dal(store_id: int, db=Depends(get_database)):
    """ 
    Get pending orders from the database. 
    """
    try:
        pending_orders = db.orders.find({"store_id": store_id, "order_status": "pending"})
        if pending_orders:
            return pending_orders
        raise HTTPException(status_code=404, detail="No pending orders found")
    except Exception as e:
        logger.error(f"Database error while fetching pending orders DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching pending orders DAL: " + str(e))

async def get_order_collection_delivered_dal(store_id: int, db=Depends(get_database)):
    """
    Get delivered orders from the database. 
    """
    try:
        delivered_orders = db.orders.find({"store_id": store_id, "order_status": "delivered"})
        if delivered_orders:
            return delivered_orders
        raise HTTPException(status_code=404, detail="No delivered orders found")
    except Exception as e:
        logger.error(f"Database error while fetching delivered orders DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching delivered orders DAL: " + str(e))

async def delete_order_collection_dal(order_id: str, db=Depends(get_database)):
    """
    Delete a specific order from the database.
    """
    try:
        delete_order = await db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"active_flag": 0}})
        if delete_order.modified_count == 1:
            return delete_order
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error while deleteing order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while deleteing order: " + str(e))