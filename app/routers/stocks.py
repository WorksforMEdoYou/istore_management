from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Stock
import logging
from ..Service.stock import create_stock_collection_bl, get_all_stocks_by_store_bl, get_stock_collection_by_id_bl, delete_stock_collection_bl
from ..db.mysql_session import get_db
from sqlalchemy.orm import Session
from ..schemas.Stock import DeleteStock, StockMessage

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stocks/", response_model=StockMessage)
async def create_stock_endpoint(stock: Stock, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        stock_data = await create_stock_collection_bl(stock, db, mysql_db)
        return stock_data
    except Exception as e:
        logger.error(f"Database error in creating the stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the stock: " + str(e))

@router.get("/stocks/list/")
async def stocks_list_endpoint(store_id: int, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        stocks_list = await get_all_stocks_by_store_bl(store_id, db, mysql_db)
        return stocks_list
    except Exception as e:
        logger.error(f"Database error in listing the stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in listing the stock: " + str(e))
    
@router.get("/stocks/medicines/")
async def stock_by_id_endpoint(store_id:int, medicine_id:int, db=Depends(get_database), mysql_db:Session=Depends(get_db)):
    try:
        medicine_stock = await get_stock_collection_by_id_bl(store_id=store_id, medicine_id=medicine_id, db=db, mysql_db=mysql_db)
        return medicine_stock
    except Exception as e:
        logger.error(f"Database error in medicnes stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in medicnes stock: " + str(e))

@router.delete("/stocks/", response_model=StockMessage)
async def delete_stock_endpoint(store:DeleteStock, db=Depends(get_database)):
    try:
        delete_stock = await delete_stock_collection_bl(store_id=store.store_id, medicine_id=store.medicine_id, db=db)
        return delete_stock
    except Exception as e:
        logger.error(f"Database error in deleting stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in deleting stock: " + str(e))