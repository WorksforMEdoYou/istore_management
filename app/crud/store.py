from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails, UpdateStoreMobile
import logging
from typing import List
from datetime import datetime
from ..db.mysql_session import get_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_store_record_db(db_store , db: Session = get_db):
    """
    Creating store record
    """
    try:
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_list_stores_db(db: Session = get_db):
    """
    Get store List active_flag==1
    """
    try:
        stores = db.query(StoreDetailsModel).filter(StoreDetailsModel.active_flag == 1).all()
        return stores
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def get_store_record_db(mobile: str, db: Session = get_db):
    """
    Get store record by mobile number
    """
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if store:
            store_details = {
                "store_id": store.store_id,
                "store_name": store.store_name,
                "license_number": store.license_number,
                "gst_state_code": store.gst_state_code,
                "gst_number": store.gst_number,
                "pan": store.pan,
                "address": store.address,
                "email": store.email,
                "mobile": store.mobile,
                "owner_name": store.owner_name,
                "is_main_store": store.is_main_store,
                "latitude": store.latitude,
                "longitude": store.longitude,
                "status": store.status,
                "remark": store.remarks,
                "verification_status": store.verification_status,
                "created_at": store.created_at,
                "updated_at": store.updated_at
            }
            return store_details
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def suspend_activate_store_db(mobile: str, remarks_text: str, active_flag_store: int, db: Session = Depends(get_db)):
    """
    Suspend or Activate Store by mobile
    """
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if store:
            store.remarks = remarks_text
            store.active_flag = active_flag_store
            store.updated_at = datetime.now()
            db.commit()
            db.refresh(store)
            return store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def verify_stores_db(mobile: str, verification: str, db: Session = Depends(get_db)):
    """
    Update verification status
    """
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if store:
            store.verification_status = verification
            store.updated_at = datetime.now()
            if verification == "verified":
                store.active_flag = 1
            db.commit()
            db.refresh(store)
            return store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def update_store_record_db(store: UpdateStoreMobile, db: Session):
    """
    Update store record by mobile
    """
    try:
        db_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == store.update_mobile).first()
        if db_store:
            db_store.store_name = store.store_name
            db_store.license_number = store.license_number
            db_store.gst_state_code = store.gst_state_code
            db_store.gst_number = store.gst_number
            db_store.pan = store.pan
            db_store.address = store.address
            db_store.email = store.email
            db_store.mobile = store.mobile
            db_store.owner_name = store.owner_name
            db_store.is_main_store = store.is_main_store
            db_store.latitude = store.latitude
            db_store.longitude = store.longitude
            db_store.status = store.status
            # Preserve existing fields
            db_store.remarks = db_store.remarks
            db_store.verification_status = db_store.verification_status
            db_store.active_flag = db_store.active_flag
            db_store.created_at = db_store.created_at
            db_store.updated_at = datetime.now()
            
            db.commit()
            db.refresh(db_store)
            return db_store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))