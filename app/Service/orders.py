from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import parse_obj_as
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Order
import logging
from datetime import datetime
from ..models.store_mysql_models import MedicineMaster
from ..utils import validate_by_id_utils
from sqlalchemy.orm import Session
from ..crud.orders import create_order_collection_dal, get_order_collection_delivered_dal, get_order_collection_pending_dal, get_order_collection_dal, delete_order_collection_dal
from ..schemas.Order import OrderMessage

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_order_collection_bl(order: Order, db=Depends(get_database)):
    """
    Create a new order in the database.
    """
    try:
        order_dict = order.dict(by_alias=True)
        create_order_data = {
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
        orders = await create_order_collection_dal(create_order_data, db)
        return OrderMessage(message="Order Created Successfully") #orders
    except Exception as e:
        logger.error(f"Database error while creating the order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the order: " + str(e))
    
async def get_order_collection_bl(store_id: int, db):
    """
    Get a specific order from the database by store.
    """
    try:
        order = await get_order_collection_dal(store_id=store_id, db=db)
        if order:    
            single_order_by_store=[]
            customer_id = str(order["customer_id"])
            customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
            if customer:
                single_order_by_store.append({
                    "order_id": str(order["_id"]),
                    "store_id": order["store_id"],
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "customer_mobile": customer["mobile"],
                    "customer_address": customer["address"],
                    "customer_doctor_name": customer.get("doctor_name", None),
                    "order_date": order["order_date"],
                    "order_status": order["order_status"],
                    "payment_method": order["payment_method"],
                    "total_amount": order["total_amount"],
                    "items": order["order_items"],
                })
            return single_order_by_store
    except Exception as e:
        logger.error(f"Database error in fetching order by store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching order by store: " + str(e))
    
async def get_order_collection_delivered_bl(store_id: int, db):
    """
    Get a specific order from the database.
    """
    try:
        orders_cursor = await get_order_collection_delivered_dal(store_id=store_id, db=db)
        orders = []
        async for order in orders_cursor:
            customer_id = str(order["customer_id"])
            customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
            if customer:
                orders.append({
                    "order_id": str(order["_id"]),
                    "store_id": order["store_id"],
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "customer_mobile": customer["mobile"],
                    "customer_address": customer["address"],
                    "customer_doctor_name": customer.get("doctor_name", None),
                    "order_date": order["order_date"],
                    "order_status": order["order_status"],
                    "payment_method": order["payment_method"],
                    "total_amount": order["total_amount"],
                    "items": order["order_items"],
                })
        if orders:
            return orders
    except Exception as e:
        logger.error(f"Database error in fetching delivered orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching delivered orders: " + str(e))

async def get_order_collection_pending_bl(store_id: int, db):
    """
    Get a specific order from the database.
    """
    try:
        orders_cursor = await get_order_collection_pending_dal(store_id=store_id, db=db)
        orders = []
        async for order in orders_cursor:
            customer_id = str(order["customer_id"])
            customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
            if customer:
                orders.append({
                    "order_id": str(order["_id"]),
                    "store_id": order["store_id"],
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "customer_mobile": customer["mobile"],
                    "customer_address": customer["address"],
                    "customer_doctor_name": customer.get("doctor_name", None),
                    "order_date": order["order_date"],
                    "order_status": order["order_status"],
                    "payment_method": order["payment_method"],
                    "total_amount": order["total_amount"],
                    "items": order["order_items"],
                })
        if orders:
            return orders
    except Exception as e:
        logger.error(f"Database error in pending orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in pending orders: " + str(e))

async def delete_order_collection_bl(order_id: str, db=Depends(get_database)):
    """
    Delete a specific order from the database.
    """
    try:
        delete_order = await delete_order_collection_dal(order_id=order_id, db=db)
        return  OrderMessage(message="Order Deleted Successfully")#delete_order
    except Exception as e:
        logger.error(f"Database error in deleting order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in deleting order: " + str(e))