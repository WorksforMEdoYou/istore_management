from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate, UpdateManufacturer
import logging
from typing import List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_manufacturer_dal(new_manufacturer_data, db: Session = get_db):
    """
    Creating manufacturer in Database 
    """
    try:
        db.add(new_manufacturer_data)
        db.commit()
        db.refresh(new_manufacturer_data)
        return new_manufacturer_data
    except Exception as e:
        logger.error(f"Database error while creating manufacturer  DAL: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating manufacturer  DAL: " + str(e))

def get_manufacturer_list_dal(db: Session):
    """
    Get list of all manufacturers
    """
    try:
        manufacturers_list = db.query(ManufacturerModel).filter(ManufacturerModel.active_flag == 1).all()
        if manufacturers_list:
            return manufacturers_list
    except Exception as e:
        logger.error(f"Database error while getting manufacturer list DAL: {e}")
        raise HTTPException(status_code=500, detail="Database error while getting manufacturer list DAL: " + str(e))

def get_manufacturer_dal(manufacturer_name: str, db: Session):
    
    """
    Get manufacturer by manufacturer_name
    """
    try:
        individual_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if individual_manufacturer:
            return individual_manufacturer
        else:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
    except Exception as e:
        logger.error(f"Database error when getting individual manufacturer  DAL: {e}")
        raise HTTPException(status_code=500, detail="Database error when getting individual manufacturer  DAL: " + str(e))

def update_manufacturer_dal(manufacturer_name: str, manufacturer: UpdateManufacturer, db: Session):
    """
    Update manufacturer by manufacturer_name
    """
    try:
        update_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if not update_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        update_manufacturer.manufacturer_name = manufacturer.manufacturer_update_name
        update_manufacturer.updated_at = datetime.now()
        db.commit()
        db.refresh(update_manufacturer)
        return update_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error when updating the manufacturer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error when updating the manufacturer: " + str(e))
    
def activate_manufacturer_dal(manufacturer_name, active_flag, db:Session):
    """
    Updating the Manufacturers active flag 0 or 1
    """
    try:
        active_inactive_manufacturer = db.query(ManufacturerModel).filter(ManufacturerModel.manufacturer_name == manufacturer_name).first()
        if not active_inactive_manufacturer:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        active_inactive_manufacturer.active_flag = active_flag
        active_inactive_manufacturer.updated_at = datetime.now()
        db.commit()
        db.refresh(active_inactive_manufacturer)
        return active_inactive_manufacturer
    except Exception as e:
        logger.error(f"Database error while updating manufacturer : {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating manufacturer : " + str(e))
        
                   