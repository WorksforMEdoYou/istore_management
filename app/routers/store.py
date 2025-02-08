from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.store_mysql_models import StoreDetails as StoreDetailsModel
from ..schemas.StoreDetailsSchema import StoreDetailsCreate, StoreDetails, StoreSuspendActivate, UpdateStoreMobile, StoreVerification, StoreMessage
import logging
from typing import List
from ..Service.store import create_store_bl, get_stores_list_bl, get_store_bl, update_store_bl, suspend_activate_store_bl, verify_stores_bl

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/stores/create/", response_model=StoreMessage, status_code=status.HTTP_201_CREATED)
def create_store_endpoint(store: StoreDetailsCreate, db: Session = Depends(get_db)):
    """
    Store Onboard Endpoint 
    """
    try:
        store_data = create_store_bl(store, db)
        return store_data
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in onboarding store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in onboarding store: " + str(e))

@router.get("/stores/list/", status_code=status.HTTP_200_OK)
def list_store_endpoint(db: Session = Depends(get_db)):
    try:
        stores_list = get_stores_list_bl(db)
        return stores_list
    except Exception as e:
        logger.error(f"Database error in list stores: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in list stores: " + str(e))

@router.get("/stores/{mobile}/", status_code=status.HTTP_200_OK)
def get_store_endpoint(mobile: str, db: Session = Depends(get_db)):
    try:
        individual_store = get_store_bl(mobile, db)
        return individual_store
    except Exception as e:
        logger.error(f"Database error in getting individual store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in getting individual store: " + str(e))

@router.put("/stores/update/", response_model=StoreMessage, status_code=status.HTTP_200_OK)
def update_store_endpoint(store: UpdateStoreMobile, db: Session = Depends(get_db)):
    try:
        update_store = update_store_bl(store, db)
        return update_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in updating store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating store: " + str(e))

@router.put("/stores/verify/", response_model=StoreMessage, status_code=status.HTTP_200_OK)
def verify_store_endpoint(verify:StoreVerification, db: Session = Depends(get_db)):
    try:
        verify_store = verify_stores_bl(mobile=verify.mobile, verification=verify.verification, db=db)
        return verify_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in verifying store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in verifying store: " + str(e))
   
@router.put("/stores/", response_model=StoreMessage, status_code=status.HTTP_200_OK)
def suspend_or_activate_store_endpoint(suspend:StoreSuspendActivate, db: Session = Depends(get_db)):
    try:
        #suspend_or_activate_store = suspend_activate_store_bl(mobile=suspend.mobile, remarks_text=suspend.remarks, active_flag_store=suspend.active_flag, db=db)
        suspend_or_activate_store = suspend_activate_store_bl(mobile=suspend.mobile, remarks_text=suspend.remarks, db=db)
        return suspend_or_activate_store
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in suspend or activate store: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in suspend or activate store: " + str(e))