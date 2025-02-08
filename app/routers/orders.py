from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import parse_obj_as
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Order
import logging
from ..Service.orders import create_order_collection_bl, get_order_collection_bl, get_order_collection_delivered_bl, get_order_collection_pending_bl, delete_order_collection_bl
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session
from ..schemas.Order import DeleteOrder, OrderMessage

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/orders/create/", response_model=OrderMessage, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(order: Order, db=Depends(get_database)):
    try:
        order_data = await create_order_collection_bl(order=order, db=db)
        return order_data
    except Exception as e:
        logger.error(f"Database error in creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating order: " + str(e))

@router.get("/orders/list", status_code=status.HTTP_200_OK)
async def get_all_store_orders_endpoint(store_id:int, db=Depends(get_database)):
    try:
        store_orders_list = await get_order_collection_bl(store_id=store_id, db=db)
        return store_orders_list
    except Exception as e:
        logger.error(f"Database error in fetching store order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching store order: " + str(e))

@router.get("/orders/pending/", status_code=status.HTTP_200_OK)
async def get_all_pending_orders_endpoint(store_id:int, db=Depends(get_database)):
    try:
        pending_orders = await get_order_collection_pending_bl(store_id=store_id, db=db)
        return pending_orders
    except Exception as e:
        logger.error(f"Database error in fetching pending order: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching pending order: " + str(e))

@router.get("/orders/delivered/", status_code=status.HTTP_200_OK)
async def get_all_delivered_orders_endpoint(store_id:int, db=Depends(get_database)):
    try:
        delivered_orders = await get_order_collection_delivered_bl(store_id=store_id, db=db)
        return delivered_orders
    except Exception as e:
        logger.error(f"Database error in fetching delivered orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching delivered orders: " + str(e))

@router.delete("/orders/delete", response_model=OrderMessage)
async def delete_order_endpoint(order:DeleteOrder, db=Depends(get_database)):
    try:
        deleted_orders = await delete_order_collection_bl(order_id=order.order_id, db=db)
        return deleted_orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))