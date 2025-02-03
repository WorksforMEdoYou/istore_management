from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.mysql import get_db
from ..models.store_mysql_models import Manufacturer as ManufacturerModel
from ..schemas.ManufacturerSchema import Manufacturer as ManufacturerSchema, ManufacturerCreate, UpdateManufacturer, ActivateManufacturer
import logging
from typing import List
from ..Service.manufacturers import create_manufacturer_record, get_manufacturer_record, update_manufacturer_record, get_manufacturer_list, activate_manufacturer_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/manufacturers/", response_model=ManufacturerSchema, status_code=status.HTTP_201_CREATED)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    try:
        db_manufacturer = create_manufacturer_record(manufacturer=manufacturer, db=db)
        return db_manufacturer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/", status_code=status.HTTP_200_OK)
def list_manufacturers(db: Session = Depends(get_db)):
    try:
        manufacturers = get_manufacturer_list(db=db)
        return manufacturers
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/manufacturers/{manufacturer_name}", status_code=status.HTTP_200_OK)
def get_manufacturer(manufacturer_name: str, db: Session = Depends(get_db)):
    try:
        manufacturer = get_manufacturer_record(manufacturer_name=manufacturer_name, db=db)
        return manufacturer
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/manufacturers/", response_model=UpdateManufacturer, status_code=status.HTTP_200_OK)
def update_manufacturer(manufacturer: UpdateManufacturer, db: Session = Depends(get_db)):
    try:
        db_manufacturer = update_manufacturer_record(manufacturer_name=manufacturer.manufacturer_update_name, manufacturer=manufacturer, db=db)
        return db_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
@router.put("/manufacturers/activate/", status_code=status.HTTP_200_OK)
def activate_deactivate(manufacturer: ActivateManufacturer, db:Session = Depends(get_db)):
    try:
        db_manufacturer = activate_manufacturer_record(manufacturer_name=manufacturer.manufacturer_name, active_flag=manufacturer.active_flag, db=db)
        return db_manufacturer
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
