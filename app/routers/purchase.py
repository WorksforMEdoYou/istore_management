from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..db.mongodb import get_database
from ..db.mysql_session import get_db
from ..models.store_mongodb_models import Purchase
import logging
from ..Service.purchase import create_purchase_collection_bl, get_all_purchase_list_bl, get_purchases_by_date_store_bl, get_purchase_collection_by_id_bl, delete_purchase_collection_bl
from ..schemas.Purchase import DeletePurchase, PurchaseMessage
from sqlalchemy.orm import Session

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/purchases/create/", response_model=PurchaseMessage, status_code=status.HTTP_201_CREATED)
async def create_purchase_endpoint(purchase: Purchase, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchase_data = await create_purchase_collection_bl(purchase, db, mysql_db=mysql_db)
        return purchase_data
    except Exception as e:
        logger.error(f"Database error in creating purchase: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating purchase: " + str(e))

@router.get("/purchase/list/", status_code=status.HTTP_200_OK)
async def get_purchase_by_id_endpoint(purchase_id:str, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchases_list = await get_purchase_collection_by_id_bl(purchase_id, db, mysql_db)
        return purchases_list
    except Exception as e:
        logger.error(f"Database error in listing the purchases by id: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in listing the purchases by id: " + str(e))

@router.get("/purchases/", status_code=status.HTTP_200_OK)
async def get_all_purchases_endpoint(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        purchases_store = await get_all_purchase_list_bl(store_id, db, mysql_db)
        return purchases_store
    except Exception as e:
        logger.error(f"Database error in fetching the purchases by store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching the purchases by store: " + str(e))

@router.get("/purchases/date/", status_code=status.HTTP_200_OK)
async def get_purchases_by_date_endpoint(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db), start_date:str=None, end_date:str=None):
    try:
        purchases_date = await get_purchases_by_date_store_bl(store_id=store_id, db=db, mysql_db=mysql_db, start_date=start_date, end_date=end_date)
        return purchases_date
    except Exception as e:
        logger.error(f"Database error in listing the purchases by date: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in listing the purchases by date: " + str(e))

@router.delete("/purchases/", response_model=PurchaseMessage)
async def delete_purchase_endpoint(delete:DeletePurchase, db=Depends(get_database)):
    try:
        deleted_purchase = await delete_purchase_collection_bl(purchase_id=delete.purchase_id, db=db)
        return deleted_purchase
    except Exception as e:
        logger.error(f"Database error in deleting purchase: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in deleting purchase: " + str(e))
    