from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from istore.app.models.store_mysql_models import StoreDetails as StoreDetailsModel
from istore.app.schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails, UpdateStoreMobile
import logging
from typing import List
from datetime import datetime
from istore.app.db.mysql_session import get_db
from istore.app.crud.store import create_store_record_db, get_list_stores_db, get_store_record_db, suspend_activate_store_db, verify_stores_db, update_store_record_db
from istore.app.utils import store_validation, store_validation_mobile

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_store_record(store: StoreDetailsCreate, db: Session = get_db):
    
    """
    Creating store record
    """
    try:
        valid_store = store_validation(store, db)
        if valid_store!="unique":
            raise HTTPException(status_code=400, detail="Store already exist")
        db_store = StoreDetailsModel(
            store_name = store.store_name,
            license_number = store.license_number,
            gst_state_code = store.gst_state_code,
            gst_number = store.gst_number,
            pan = store.pan,
            address = store.address,
            email = store.email,
            mobile = store.mobile,
            owner_name = store.owner_name,
            is_main_store = store.is_main_store,
            latitude = store.latitude,
            longitude = store.longitude,
            status = store.status,
            remarks = "",
            verification_status = "pending",
            active_flag = 0,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        result = create_store_record_db(db_store, db)
        return result
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_list_stores(db: Session = get_db):
    """
    Get store List active_flag==1
    """
    try:
        stores = get_list_stores_db(db)
        return stores
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def get_store_record(mobile: str, db: Session = get_db):
    """
    Get store record by store_id
    """
    try:
        valid_store = store_validation_mobile(mobile, db)
        if valid_store=="unique":
            raise HTTPException(status_code=400, detail="Store not found")
        store_details = get_store_record_db(mobile, db)
        return store_details
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def suspend_activate_store(mobile: str, remarks_text: str, active_flag_store: int, db: Session = Depends(get_db)):
    """
    Suspend or Activate Store by mobile
    """
    try:
        store_valid = store_validation_mobile(mobile, db)
        if store_valid == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        
        store = suspend_activate_store_db(mobile, remarks_text, active_flag_store, db)
        return store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def verify_stores(mobile: str, verification: str, db: Session = Depends(get_db)):
    """
    Verify store and update verification status
    """
    try:
        store_valid = store_validation_mobile(mobile, db)
        if store_valid == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        
        store = verify_stores_db(mobile, verification, db)
        return store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def map_store_details_to_update_store_mobile(store: StoreDetailsModel, update_mobile: str) -> UpdateStoreMobile:
    return UpdateStoreMobile(
        store_name=store.store_name,
        license_number=store.license_number,
        gst_state_code=store.gst_state_code,
        gst_number=store.gst_number,
        pan=store.pan,
        address=store.address,
        email=store.email,
        mobile=store.mobile,
        owner_name=store.owner_name,
        is_main_store=store.is_main_store,
        latitude=store.latitude,
        longitude=store.longitude,
        status=store.status,
        update_mobile=update_mobile
    )

def update_store_record(store: UpdateStoreMobile, db: Session):
    """
    Update store record by mobile
    """
    try:
        store_valid = store_validation_mobile(store.update_mobile, db)
        if store_valid == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        db_store = update_store_record_db(store, db)
        return map_store_details_to_update_store_mobile(db_store, store.update_mobile)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
