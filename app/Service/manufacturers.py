from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate
import logging
from typing import List
from datetime import datetime
from ..utils import check_name_available
from ..crud.manufacturers import create_manufacturer_record_db, get_manufacturer_list_db, get_manufacturer_record_db, update_manufacturer_record_db, activate_manufacturer_record_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_manufacturer_record(manufacturer:ManufacturerCreate, db: Session = get_db):
    """
    Creating manufacturer record
    """
    try:
        manufacturer_available = check_name_available(name=manufacturer.manufacturer_name, model=ManufacturerModel, field="manufacturer_name", db=db)
        if manufacturer_available != "unique":
            raise HTTPException(status_code=400, detail="Manufacturer already exists")
        
        db_manufacturer = ManufacturerModel(
            manufacturer_name = manufacturer.manufacturer_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        result = create_manufacturer_record_db(db_manufacturer, db)
        return result
    except Exception as e:
        logger.error(f"Error creating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating manufacturer record: " + str(e))

def get_manufacturer_list(db: Session):
    """
    Get list of all manufacturers
    """
    try:
        manufacturer_list = get_manufacturer_list_db(db)
        return manufacturer_list
    except Exception as e:
        logger.error(f"Error getting manufacturer list: {e}")
        raise HTTPException(status_code=500, detail="Error getting manufacturer list: " + str(e))

def get_manufacturer_record(manufacturer_name: str, db: Session):
    
    """
    Get manufacturer record by manufacturer_id
    """
    try:
        manufacturer_valid = check_name_available(name=manufacturer_name, model=ManufacturerModel, field="manufacturer_name", db=db)
        if manufacturer_valid == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        manufacturer = get_manufacturer_record_db(manufacturer_name, db)
        return manufacturer
    except Exception as e:
        logger.error(f"Error getting manufacturer record: {e}")
        raise HTTPException(status_code=500, detail="Error getting manufacturer record: " + str(e))

def update_manufacturer_record(manufacturer_name: str, manufacturer: ManufacturerCreate, db: Session):
    """
    Update manufacturer record by manufacturer_name
    """
    try:
        manufacturer_valid = check_name_available(name=manufacturer_name, model=ManufacturerModel, field="manufacturer_name", db=db)
        if manufacturer_valid == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        
        db_manufacturer = update_manufacturer_record_db(manufacturer_name, manufacturer, db)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error updating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating manufacturer record: " + str(e))

def activate_manufacturer_record(manufacturer_name, active_flag, db:Session):
    """
    Updating the Manufacturers active flag 0 or 1
    """
    try:
        manufacturer_valid = check_name_available(name=manufacturer_name, model=ManufacturerModel, field="manufacturer_name", db=db)
        if manufacturer_valid == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        db_manufacturer = activate_manufacturer_record_db(manufacturer_name, active_flag, db)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error updating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating manufacturer record: " + str(e))
        
                   