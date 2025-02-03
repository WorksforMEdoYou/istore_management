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

async def create_order_collection_db(order, db=Depends(get_database)):
    """
    Create a new order in the database.
    """
    try:
        result = await db.orders.insert_one(order)
        order["_id"] = str(result.inserted_id)
        logger.info(f"Order created with ID: {order['_id']}")
        return order
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_order_collection_db(store_id: int, db=Depends(get_database)):
    """ Get a specific order from the database. """
    try:
        order = await db.orders.find_one({"store_id": store_id})
        if order:
            customer_id = str(order["customer_id"])
            customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
            if customer:
                return {
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
                }
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_order_collection_pending_db(store_id: int, db=Depends(get_database)):
    """ Get pending orders from the database. """
    try:
        orders_cursor = db.orders.find({"store_id": store_id, "order_status": "pending"})
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
        raise HTTPException(status_code=404, detail="No pending orders found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_order_collection_delivered_db(store_id: int, db=Depends(get_database)):
    """ Get delivered orders from the database. """
    try:
        orders_cursor = db.orders.find({"store_id": store_id, "order_status": "delivered"})
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
        raise HTTPException(status_code=404, detail="No delivered orders found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_order_collection_db(order_id: str, db=Depends(get_database)):
    """
    Delete a specific order from the database.
    """
    try:
        delete_result = await db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"active_flag": 0}})
        if delete_result.modified_count == 1:
            return {"message": "Order deleted successfully"}
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))