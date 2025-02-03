from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..db.mongodb import get_database
from ..db.mysql_session import get_db
from ..models.store_mongodb_models import Purchase
import logging
from ..Service.purchase import create_purchase_collection, get_all_purchase_list, get_purchase_collection_by_id, get_purchases_by_date_store, delete_purchase_collection
from ..schemas.Purchase import DeletePurchase
from sqlalchemy.orm import Session

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/purchases/", response_model=Purchase, status_code=status.HTTP_201_CREATED)
async def create_purchase(purchase: Purchase, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchase_dict = await create_purchase_collection(purchase, db, mysql_db=mysql_db)
        return purchase_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/purchase/", status_code=status.HTTP_200_OK)
async def get_purchase_by_id(purchase_id:str, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchases = await get_purchase_collection_by_id(purchase_id, db, mysql_db)
        return purchases
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/purchases/", status_code=status.HTTP_200_OK)
async def get_all_purchases(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchases = await get_all_purchase_list(store_id, db, mysql_db)
        return purchases
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/purchases/date/", status_code=status.HTTP_200_OK)
async def get_purchases_by_date(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db), start_date:str=None, end_date:str=None):
    try:
        purchases = await get_purchases_by_date_store(store_id=store_id, db=db, mysql_db=mysql_db, start_date=start_date, end_date=end_date)
        return purchases
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/purchases/", response_model=DeletePurchase)
async def delete_purchase(delete:DeletePurchase, db=Depends(get_database)):
    try:
        delete_result = await delete_purchase_collection(purchase_id=delete.purchase_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    