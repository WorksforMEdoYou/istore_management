from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.store_mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails
import logging
from typing import List
from ..Service.store import create_store_record, get_list_stores, get_store_record, update_store_record, suspend_activate_store, verify_stores

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stores/", response_model=StoreDetails, status_code=status.HTTP_201_CREATED)
def add_store(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = create_store_record(store, db)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/", status_code=status.HTTP_200_OK)
def list_stores(db: Session = Depends(get_db)):
    try:
        stores = get_list_stores(db)
        return stores
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/stores/{mobile}", status_code=status.HTTP_200_OK)
def get_store(mobile: str, db: Session = Depends(get_db)):
    try:
        store = get_store_record(mobile, db)
        return store
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stores/update/{mobile}", response_model=StoreDetails, status_code=status.HTTP_200_OK)
def update_store(mobile: str, store: StoreDetailsCreate, db: Session = Depends(get_db)):
    try:
        db_store = update_store_record(mobile, store, db)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/stores/verify/{mobile}", status_code=status.HTTP_200_OK)
def verify_store(mobile: str, verification: str, db: Session = Depends(get_db)):
    try:
        db_store = verify_stores(mobile, verification, db)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
   
@router.put("/stores/{mobile}", status_code=status.HTTP_200_OK)
def suspend_activate(mobile:str, remarks:str, active_flag:int, db: Session = Depends(get_db)):
    try:
        db_store = suspend_activate_store(mobile, remarks, active_flag, db)
        return db_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))