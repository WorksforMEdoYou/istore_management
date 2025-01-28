from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from ..models.store_mysql_models import Category 
from ..models.store_mysql_models import Manufacturer
from ..schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ..utils import check_name_available
from ..crud.medicine_master import create_medicine_master_record_db, get_medicine_list_db, get_medicine_master_record_db, update_medicine_master_record_db, activate_medicine_record_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_medicine_master_record(medicine_master: MedicineMasterCreate, db: Session):
    """
    Creating medicine_master record
    """
    try:
        # Validate category_id
        if not check_name_available(name=medicine_master.category_id, model=MedicineMasterModel, field="category_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not check_name_available(name=medicine_master.manufacturer_id, model=MedicineMasterModel, field="manufacturer_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        # Validate Medicine name is Available
        validate_medicine_name_available = check_name_available(name=medicine_master.medicine_name, model=MedicineMasterModel, field="medicine_name", db=db)
        if validate_medicine_name_available != "unique":
            raise HTTPException(status_code=400, detail="Medicine already exists")
        
        db_medicine_master = MedicineMasterModel(
            medicine_name = medicine_master.medicine_name,
            generic_name = medicine_master.generic_name,
            hsn_code = medicine_master.hsn_code,
            formulation = medicine_master.formulation,
            strength = medicine_master.strength,
            unit_of_measure = medicine_master.unit_of_measure,
            manufacturer_id = medicine_master.manufacturer_id,
            category_id = medicine_master.category_id,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        result = create_medicine_master_record_db(db_medicine_master, db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_list(db:Session):
    """
    Get Medicine list by active_flag=1
    """
    try:
        medicines_list = get_medicine_list_db(db)
        return medicines_list
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_master_record(medicine_name: str, db: Session):
    
    """
    Get medicine_master record by medicine_id
    """
    try:
        validate_medicine_name_available = check_name_available(name=medicine_name, model=MedicineMasterModel, field="medicine_name", db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine Not found")
        medicine_master = get_medicine_master_record_db(medicine_name, db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def update_medicine_master_record(medicine_name: str, medicine_master: MedicineMasterCreate, db: Session):
    
    """
    Update medicine_master record by medicine_id
    """
    try:
        # Validate by medicine_name
        validate_medicine_name_available = check_name_available(name=medicine_name, model=MedicineMasterModel, field="medicine_name", db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        
        # Validate category_id
        if not check_name_available(name=medicine_master.category_id, model=MedicineMasterModel, field="category_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not check_name_available(name=medicine_master.manufacturer_id, model=MedicineMasterModel, field="manufacturer_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        db_medicine_master = update_medicine_master_record_db(medicine_name, medicine_master, db)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def activate_medicine_record(medicine_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        validate_medicine_name_available = check_name_available(name=medicine_name, model=MedicineMasterModel, field="medicine_name", db=db)
        if validate_medicine_name_available=="unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        db_medicine_master = activate_medicine_record_db(medicine_name, active_flag, db)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

        