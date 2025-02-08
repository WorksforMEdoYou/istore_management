from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate, UpdateManufacturer, ActivateManufacturer, ManufacturerMessage
import logging
from typing import List
from ..Service.manufacturers import create_manufacturer_bl, get_manufacturer_bl, update_manufacturer_bl, get_list_manufacturers_bl, activate_manufacturer_bl

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/manufacturers/create/", response_model=ManufacturerMessage, status_code=status.HTTP_201_CREATED)
def create_manufacturer_endpoint(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        manufacturer_data = create_manufacturer_bl(manufacturer=manufacturer, db=db)
        return manufacturer_data
    except Exception as e:
        logger.error(f"Database error in creating manufacturer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating manufacturer: " + str(e))

@router.get("/manufacturers/", status_code=status.HTTP_200_OK)
def list_manufacturers_endpoint(db: Session = Depends(get_db)):
    try:
        manufacturers_list = get_list_manufacturers_bl(db=db)
        return manufacturers_list
    except Exception as e:
        logger.error(f"Database error in fetching manufacturers list: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching manufacturers list: " + str(e))

@router.get("/manufacturers/{manufacturer_name}", status_code=status.HTTP_200_OK)
def get_manufacturer_endpoint(manufacturer_name: str, db: Session = Depends(get_db)):
    try:
        individual_manufacturer = get_manufacturer_bl(manufacturer_name=manufacturer_name, db=db)
        return individual_manufacturer
    except Exception as e:
        logger.error(f"Database error in fetching manufacturer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching manufacturer: " + str(e))

@router.put("/manufacturers/", response_model=ManufacturerMessage, status_code=status.HTTP_200_OK)
def update_manufacturer_endpoint(manufacturer: UpdateManufacturer, db: Session = Depends(get_db)):
    try:
        db_manufacturer = update_manufacturer_bl(manufacturer_name=manufacturer.manufacturer_update_name, manufacturer=manufacturer, db=db)
        return db_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in updating manufacturer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating manufacturer: " + str(e))
    
@router.put("/manufacturers/activate/", response_model=ManufacturerMessage, status_code=status.HTTP_200_OK)
def activate_deactivate_endpoint(manufacturer: ActivateManufacturer, db:Session = Depends(get_db)):
    try:
        activate_deactivate_manufacturer = activate_manufacturer_bl(manufacturer_name=manufacturer.manufacturer_name, active_flag=manufacturer.active_flag, db=db)
        return activate_deactivate_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activating or inactivating manufacturer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activating or inactivating manufacturer: " + str(e))
