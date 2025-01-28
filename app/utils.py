from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
import logging
from .db.mysql_session import get_db
from .models.store_mysql_models import StoreDetails as StoreDetailsModel
from .schemas.StoreDetailsSchema import StoreDetailsCreate

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_name_available(name:str, model, field:str, db:Session):
    """
    Checking the field available in the model
    """
    try:
        name = db.query(model).filter(getattr(model, field) == name).first()
        if name:
            return name
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def store_validation(store: StoreDetailsCreate, db: Session):
    """
    Store validation by email or mobile
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            or_(
            StoreDetailsModel.email == store.email,
            StoreDetailsModel.mobile == store.mobile
            )).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
# cheacking wether the store is allready present in the database
def store_validation_mobile(mobile:str, db: Session = get_db):
    """
    Store validation by mobile number
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            StoreDetailsModel.mobile == mobile
            ).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    