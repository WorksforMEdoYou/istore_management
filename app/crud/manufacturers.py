from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate
import logging
from typing import List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_manufacturer_record_db(db_manufacturer, db: Session = get_db):
    """
    Creating manufacturer record
    """
    try:
        db.add(db_manufacturer)
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error creating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating manufacturer record: " + str(e))

def get_manufacturer_list_db(db: Session):
    """
    Get list of all manufacturers
    """
    try:
        manufacturers = db.query(ManufacturerModel).filter(ManufacturerModel.active_flag == 1).all()
        manufacturer_list = []
        for manufacturer in manufacturers:
            manufacturer_data = {
                "manufacturer_id": manufacturer.manufacturer_id,
                "manufacturer_name": manufacturer.manufacturer_name,
                "created_at": manufacturer.created_at,
                "updated_at": manufacturer.updated_at,
                "active_flag": manufacturer.active_flag
            }
            manufacturer_list.append(manufacturer_data)
        return manufacturer_list
    except Exception as e:
        logger.error(f"Error getting manufacturer list: {e}")
        raise HTTPException(status_code=500, detail="Error getting manufacturer list: " + str(e))

def get_manufacturer_record_db(manufacturer_name: str, db: Session):
    
    """
    Get manufacturer record by manufacturer_id
    """
    try:
        manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if manufacturer:
            return manufacturer
        else:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
    except Exception as e:
        logger.error(f"Error getting manufacturer record: {e}")
        raise HTTPException(status_code=500, detail="Error getting manufacturer record: " + str(e))

def update_manufacturer_record_db(manufacturer_name: str, manufacturer: ManufacturerCreate, db: Session):
    """
    Update manufacturer record by manufacturer_name
    """
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        db_manufacturer.manufacturer_name = manufacturer.manufacturer_name
        db_manufacturer.updated_at = datetime.now()
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error updating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating manufacturer record: " + str(e))

def activate_manufacturer_record_db(manufacturer_name, active_flag, db:Session):
    """
    Updating the Manufacturers active flag 0 or 1
    """
    try:
        db_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if not db_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        db_manufacturer.active_flag = active_flag
        db_manufacturer.updated_at = datetime.now()
        db.commit()
        db.refresh(db_manufacturer)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Error updating manufacturer record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating manufacturer record: " + str(e))
        
                   