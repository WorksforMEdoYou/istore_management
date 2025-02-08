from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails, UpdateStoreMobile, StoreMessage
import logging
from typing import List
from datetime import datetime
from ..db.mysql_session import get_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_store_dal(new_store_data_dal , db: Session = get_db):
    """
    Onboarding The Store In Database
    """
    try:
        db.add(new_store_data_dal)
        db.commit()
        db.refresh(new_store_data_dal)
        return new_store_data_dal
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while onboarding the store DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while onboarding the store DAL: " + str(e))

def get_list_stores_dal(db: Session = get_db):
    """
    Get store List
    """
    try:
        #stores_list_dal = db.query(StoreDetailsModel).filter(StoreDetailsModel.active_flag == 1).all()
        stores_list_dal = db.query(StoreDetailsModel).all()
        return stores_list_dal
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching the stores list DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the stores list DAL:" + str(e))
    
def get_store_dal(mobile: str, db: Session = get_db):
    """
    Get store  by mobile number
    """
    try:
        store_dal = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if store_dal:
            return store_dal
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching the store using mobile number DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
#def suspend_activate_store_dal(mobile: str, remarks_text: str, active_flag_store: int, db: Session = Depends(get_db)):
def suspend_activate_store_dal(mobile: str, remarks_text: str, db: Session = Depends(get_db)):
    """
    Suspend or Activate Store by mobile number
    """
    try:
        store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if store:
            store.remarks = remarks_text
            #store.active_flag = active_flag_store
            store.active_flag = 2 # 2 suspend
            store.updated_at = datetime.now()
            db.commit()
            db.refresh(store)
            return store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while suspend or activate the strore DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while suspend or activate the strore DAL: " + str(e))

def verify_store_dal(mobile: str, verification: str, db: Session = Depends(get_db)):
    """
    Update verification status of the store using mobile number
    """
    try:
        verify_store = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == mobile).first()
        if verify_store:
            verify_store.verification_status = verification
            verify_store.updated_at = datetime.now()
            if verification == "verified":
                verify_store.active_flag = 1
            db.commit()
            db.refresh(verify_store)
            return verify_store
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while verification DAL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while verification DAL: " + str(e))

def update_store_dal(store: UpdateStoreMobile, db: Session):
    """
    Update store  by mobile number
    """
    try:
        store_update = db.query(StoreDetailsModel).filter(StoreDetailsModel.mobile == store.mobile).first()
        if store_update:
            store_update.store_name = store.store_name
            store_update.license_number = store.license_number
            store_update.gst_state_code = store.gst_state_code
            store_update.gst_number = store.gst_number
            store_update.pan = store.pan
            store_update.address = store.address
            store_update.email = store.email
            store_update.owner_name = store.owner_name
            store_update.is_main_store = store.is_main_store
            store_update.latitude = store.latitude
            store_update.longitude = store.longitude
            store_update.status = store.status
            # Preserve existing fields
            store_update.mobile = store_update.mobile
            store_update.remarks = store_update.remarks
            store_update.verification_status = store_update.verification_status
            store_update.active_flag = store_update.active_flag
            store_update.created_at = store_update.created_at
            store_update.updated_at = datetime.now()
            
            db.commit()
            db.refresh(store_update)
            return store_update
        else:
            raise HTTPException(status_code=404, detail="Store not found")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating the store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating the store: " + str(e))