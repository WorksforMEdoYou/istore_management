from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from istore.app.models.store_mysql_models import StoreDetails as StoreDetailsModel
from istore.app.schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails, UpdateStoreMobile, StoreMessage
import logging
from typing import List
from datetime import datetime
from istore.app.db.mysql_session import get_db
from istore.app.crud.store import create_store_dal, get_list_stores_dal, get_store_dal, update_store_dal, verify_store_dal, suspend_activate_store_dal
from istore.app.utils import check_store_exists_utils, store_validation_mobile_utils

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_store_bl(store: StoreDetailsCreate, db: Session = get_db):
    
    """
    Onboarding Store BL
    """
    try:
        store_exists = check_store_exists_utils(store, db)
        if store_exists!="unique":
            raise HTTPException(status_code=400, detail="Store already exist")
        new_store_data = StoreDetailsModel(
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
            #status = store.status,
            remarks = "",
            verification_status = "pending",
            active_flag = 0,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        #this will hold all the data form the created store
        onboarded_store_data = create_store_dal(new_store_data, db)
        return StoreMessage(message="Store Onboarded Successfully") #onboarded_store_data
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in Onboarding store BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in Onbarding store BL: " + str(e))

def get_stores_list_bl(db: Session = get_db):
    """
    Get the list store active_flag==1 BL
    """
    try:
        stores_list = get_list_stores_dal(db)
        return stores_list
    except SQLAlchemyError as e:
        logger.error(f"Database error in fetching store list BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching store list BL: " + str(e))
    
def get_store_bl(mobile: str, db: Session = get_db):
    """
    Get store  by mobile number BL
    """
    try:
        valid_store = store_validation_mobile_utils(mobile, db)
        if valid_store=="unique":
            raise HTTPException(status_code=400, detail="Store not found")
        store = get_store_dal(mobile, db)
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
        logger.error(f"Database error in fetching the store by mobile BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching the store by mobile BL: " + str(e))
    
#def suspend_activate_store_bl(mobile: str, remarks_text: str, active_flag_store: int, db: Session = Depends(get_db)):
def suspend_activate_store_bl(mobile: str, remarks_text: str, db: Session = Depends(get_db)):
    """
    Suspend or Activate Store by mobile BL making active_status = 2
    """
    try:
        store_valid = store_validation_mobile_utils(mobile, db)
        if store_valid == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # this will hold the data from the suspended or activated store
        #store_suspend_acivate = suspend_activate_store_dal(mobile, remarks_text, active_flag_store, db)
        store_suspend_acivate = suspend_activate_store_dal(mobile, remarks_text, db)
        #if active_flag_store == 1:
            #return StoreMessage(message="Store activated successfully")
        return StoreMessage(message="Store suspended successfully")#store_suspend_acivate
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in suspending or activating BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in suspending or activating BL: " + str(e))

def verify_stores_bl(mobile: str, verification: str, db: Session = Depends(get_db)):
    """
    Verify store and update verification status
    """
    try:
        store_exists = store_validation_mobile_utils(mobile, db)
        if store_exists == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        #this will hold the data from the verified store
        store = verify_store_dal(mobile, verification, db)
        return StoreMessage(message="Store Verified Successfully") #store_verification
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in store verification BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in store verification BL: " + str(e))

def update_store_bl(store: UpdateStoreMobile, db: Session):
    """
    Update store  by mobile number BL
    """
    try:
        store_exists = store_validation_mobile_utils(store.mobile, db)
        if store_exists == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # this will hold all the data from the updated store
        db_store = update_store_dal(store, db)
        return StoreMessage(message="Store Updated successfully") #db_store
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in updating the store details BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating the store details BL: " + str(e))
