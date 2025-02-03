from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Stock
import logging
from ..Service.stock import create_stock_collection, get_all_stocks_by_store, get_stock_collection_by_id, delete_stock_collection
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session
from ..schemas.Stock import DeleteStock

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stocks/", response_model=Stock)
async def create_stock(stock: Stock, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        stock_dict = await create_stock_collection(stock, db, mysql_db)
        return stock_dict
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stocks/")
async def read_stocks(store_id: int, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        stocks = await get_all_stocks_by_store(store_id, db, mysql_db)
        return stocks
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
@router.get("/stocks/medicines/")
async def read_stock(store_id:int, medicine_id:int, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        stock = await get_stock_collection_by_id(store_id=store_id, medicine_id=medicine_id, db=db, mysql_db=mysql_db)
        return stock
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/stocks/", response_model=DeleteStock)
async def delete_stock(store:DeleteStock, db=Depends(get_database)):
    try:
        delete_result = await delete_stock_collection(store_id=store.store_id, medicine_id=store.medicine_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))