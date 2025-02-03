from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from ..Service.sale import create_sale_collection, get_sale_particular, get_sales, delete_sale_collection 
from ..schemas.Sale import DeleteSale
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/sales/", response_model=Sale, status_code=status.HTTP_201_CREATED)
async def create_sale_order(sale: Sale, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        sale_dict = await create_sale_collection(sale, db, mysql_db)
        return sale_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/sales/list/", status_code=status.HTTP_200_OK)
async def read_sales(store_id:int, db=Depends(get_database)):
    try:
        sales = await get_sales(store_id=store_id, db=db)
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/sales/", response_model=Sale, status_code=status.HTTP_200_OK)
async def get_sale_order(sale_id: str, db=Depends(get_database)):
    try:
        sale = await get_sale_particular(sale_id, db)
        return sale
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/sales/", response_model=DeleteSale, status_code=status.HTTP_200_OK)
async def delete_sale_order(sale: DeleteSale, db=Depends(get_database)):
    try:
        delete_result = await delete_sale_collection(sale_id=sale.sale_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    