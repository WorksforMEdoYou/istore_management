from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate, UpdateManufacturer, ManufacturerMessage
import logging
from typing import List
from datetime import datetime
from ..utils import check_name_available_utils
from ..crud.manufacturers import create_manufacturer_dal, get_manufacturer_dal, get_manufacturer_list_dal, update_manufacturer_dal, activate_manufacturer_dal

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_manufacturer_bl(manufacturer:ManufacturerCreate, db: Session = get_db):
    """
    Creating manufacturer BL
    """
    try:
        check_manufacturer_exists = check_name_available_utils(name=manufacturer.manufacturer_name, table=ManufacturerModel, field="manufacturer_name", db=db)
        if check_manufacturer_exists != "unique":
            raise HTTPException(status_code=400, detail="Manufacturer already exists")
        
        new_manufacturer_data = ManufacturerModel(
            manufacturer_name = manufacturer.manufacturer_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        # this will hold the data of new manufacturer
        created_manufacturer_data = create_manufacturer_dal(new_manufacturer_data, db)
        return ManufacturerMessage(message="Manufacturer Created Successfully") #created_manufacturer_data
    except Exception as e:
        logger.error(f"Database error in creating manufacturer  BL: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error in creating manufacturer  BL: " + str(e))

def get_list_manufacturers_bl(db: Session):
    """
    Get list of all manufacturers BL
    """
    try:
        manufacturers = get_manufacturer_list_dal(db)
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
        logger.error(f"Database error in getting manufacturer list BL: {e}")
        raise HTTPException(status_code=500, detail="Database error in getting manufacturer list BL: " + str(e))

def get_manufacturer_bl(manufacturer_name: str, db: Session):
    
    """
    Get manufacturer  by manufacturer_name BL
    """
    try:
        check_manufacturer_exists = check_name_available_utils(name=manufacturer_name, table=ManufacturerModel, field="manufacturer_name", db=db)
        if check_manufacturer_exists == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        individual_manufacturer = get_manufacturer_dal(manufacturer_name, db)
        return individual_manufacturer
    except Exception as e:
        logger.error(f"Database error getting manufacturer  BL: {e}")
        raise HTTPException(status_code=500, detail="Database error getting manufacturer  BL: " + str(e))

def update_manufacturer_bl(manufacturer_name: str, manufacturer: ManufacturerCreate, db: Session):
    """
    Update manufacturer  by manufacturer_name BL
    """
    try:
        check_manufacturer_exists = check_name_available_utils(name=manufacturer_name, table=ManufacturerModel, field="manufacturer_name", db=db)
        if check_manufacturer_exists == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        # this will hold the data of the updated mainufacturer
        updated_manufacturer = update_manufacturer_dal(manufacturer_name, manufacturer, db)
        return ManufacturerMessage(message="manufacturer Updated Successfully")
    except Exception as e:
        logger.error(f"Database error updating manufacturer : {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error updating manufacturer : " + str(e))

def activate_manufacturer_bl(manufacturer_name, active_flag, db:Session):
    """
    Updating the Manufacturers active flag 0 or 1 BL
    """
    try:
        check_manufacturer_exists = check_name_available_utils(name=manufacturer_name, table=ManufacturerModel, field="manufacturer_name", db=db)
        if check_manufacturer_exists == "unique":
            raise HTTPException(status_code=400, detail="Manufacturer not found")
        # this will hold the data for the updated manufacturer
        activated_inactivated_manufacturer = activate_manufacturer_dal(manufacturer_name, active_flag, db)
        if active_flag==1:
            return ManufacturerMessage(message="Manufacturer Activated Successfully")
        return ManufacturerMessage(message="Manufacturer Inactivated Successfully")
        #activated_inactivated_manufacturer
    except Exception as e:
        logger.error(f"Database error updating manufacturer : {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error updating manufacturer : " + str(e))
                        