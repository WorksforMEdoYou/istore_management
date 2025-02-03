from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
from ..schemas.Pricing import UpdatePricing, DeletePricing
from ..Service.pricing import create_pricing_collection, get_all_collection, delete_pricing_collection
import logging
from ..db.mysql_session import get_db

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/pricing/", response_model=Pricing, status_code=status.HTTP_201_CREATED)
async def create_pricing(pricing: Pricing, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        pricing_dict = await create_pricing_collection(pricing, db, mysql_db)
        return pricing_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/pricings/", status_code=status.HTTP_200_OK)
async def list_pricing(store_id: int, medicine_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        pricing_list = await get_all_collection(store_id=store_id, medicine_id=medicine_id, db=db, mysql_db=mysql_db)
        return pricing_list
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/pricing/", response_model=DeletePricing, status_code=status.HTTP_200_OK)
async def delete_pricing(pricing: DeletePricing, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        delete_result = await delete_pricing_collection(store_id=pricing.store_id, medicine_id=pricing.medicine_id, db=db, mysql_db=mysql_db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))