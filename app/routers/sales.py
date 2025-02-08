from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from ..Service.sale import create_sale_collection_bl, get_sale_particular_bl, get_sales_bl, delete_sale_collection_bl 
from ..schemas.Sale import DeleteSale, SaleMessage
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/sales/create/", response_model=SaleMessage, status_code=status.HTTP_201_CREATED)
async def create_sale_order_endpoint(sale: Sale, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        sale_data = await create_sale_collection_bl(sale, db, mysql_db)
        return sale_data
    except Exception as e:
        logger.error(f"Database error in creating the sale: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the sale: " + str(e))

@router.get("/sales/list/", status_code=status.HTTP_200_OK)
async def read_sales_endpoint(store_id:int, db=Depends(get_database)):
    try:
        sales_list = await get_sales_bl(store_id=store_id, db=db)
        return sales_list
    except Exception as e:
        logger.error(f"Database error in listing the sale: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in listing the sale: " + str(e))

@router.get("/sales/", response_model=Sale, status_code=status.HTTP_200_OK)
async def get_sale_order_endpoint(sale_id: str, db=Depends(get_database)):
    try:
        individual_sale = await get_sale_particular_bl(sale_id, db)
        return individual_sale
    except Exception as e:
        logger.error(f"Database error in fetching individual store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching individual store: " + str(e))

@router.delete("/sales/delete/", response_model=SaleMessage, status_code=status.HTTP_200_OK)
async def delete_sale_order_endpoint(sale: DeleteSale, db=Depends(get_database)):
    try:
        delete_sale = await delete_sale_collection_bl(sale_id=sale.sale_id, db=db)
        return delete_sale
    except Exception as e:
        logger.error(f"Database error in delete sale: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in delete sale: " + str(e))
    