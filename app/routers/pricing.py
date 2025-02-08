from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
from ..schemas.Pricing import UpdatePricing, DeletePricing, PricingMessage
from ..Service.pricing import create_pricing_collection_bl, get_all_pricing_collection_list_bl, update_pricing_logic_bl, delete_pricing_collection_bl
import logging
from ..db.mysql_session import get_db

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/pricing/create/", response_model=PricingMessage, status_code=status.HTTP_201_CREATED)
async def create_pricing_endpoint(pricing: Pricing, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        pricing_data = await create_pricing_collection_bl(pricing, db, mysql_db)
        return pricing_data
    except Exception as e:
        logger.error(f"Database error in creating the pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the pricing: " + str(e))

@router.get("/pricings/", status_code=status.HTTP_200_OK)
async def list_pricing_endpoint(store_id: int, medicine_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        pricing_list = await get_all_pricing_collection_list_bl(store_id=store_id, medicine_id=medicine_id, db=db, mysql_db=mysql_db)
        return pricing_list
    except Exception as e:
        logger.error(f"Database error in list pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in list pricing: " + str(e))
    
@router.put("/pricing/edit/", response_model=PricingMessage, status_code=status.HTTP_200_OK)
async def update_pricing_endpoint(pricing: UpdatePricing, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        update_pricing = await update_pricing_logic_bl(pricing, db, mysql_db)
        return update_pricing
    except Exception as e:
        logger.error(f"Database error in updating pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating pricing: " + str(e))

@router.delete("/pricing/delete/", response_model=PricingMessage, status_code=status.HTTP_200_OK)
async def delete_pricing_endpoint(pricing: DeletePricing, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    try:
        delete_pricing = await delete_pricing_collection_bl(store_id=pricing.store_id, medicine_id=pricing.medicine_id, db=db, mysql_db=mysql_db)
        return delete_pricing
    except Exception as e:
        logger.error(f"Database error in delete pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in delete pricing: " + str(e))