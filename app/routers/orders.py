from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import parse_obj_as
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Order
import logging
from ..Service.orders import create_order_collection, get_order_collection, delete_order_collection, get_order_collection_delivered, get_order_collection_pending
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session
from ..schemas.Order import DeleteOrder

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/orders/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: Order, db=Depends(get_database)):
    try:
        order_dict = await create_order_collection(order=order, db=db)
        return order_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/", status_code=status.HTTP_200_OK)
async def get_all_orders(store_id:int, db=Depends(get_database)):
    try:
        orders = await get_order_collection(store_id=store_id, db=db)
        return orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/pending/", status_code=status.HTTP_200_OK)
async def get_all_orders(store_id:int, db=Depends(get_database)):
    try:
        orders = await get_order_collection_pending(store_id=store_id, db=db)
        return orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/orders/delivered/", status_code=status.HTTP_200_OK)
async def get_all_orders(store_id:int, db=Depends(get_database)):
    try:
        orders = await get_order_collection_delivered(store_id=store_id, db=db)
        return orders
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@router.delete("/orders/", response_model=dict)
async def delete_order(order:DeleteOrder, db=Depends(get_database)):
    try:
        delete_result = await delete_order_collection(order_id=order.order_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))