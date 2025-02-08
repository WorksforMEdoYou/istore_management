from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from ..models.store_mysql_models import Category 
from ..models.store_mysql_models import Manufacturer
from ..schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate, UpdateMedicine, MedicineMasterMessage
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ..utils import check_name_available_utils
from ..crud.medicine_master import create_medicine_master_dal, get_medicine_master_dal, get_medicine_list_dal, update_medicine_master_dal, activate_medicine_dal

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_medicine_master_bl(medicine_master: MedicineMasterCreate, db: Session):
    """
    Creating medicine_master BL
    """
    try:
        # Validate category_id
        if not check_name_available_utils(name=medicine_master.category_id, table=MedicineMasterModel, field="category_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not check_name_available_utils(name=medicine_master.manufacturer_id, table=MedicineMasterModel, field="manufacturer_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        
        # Validate Medicine name is Available
        check_medicine_name_exists = check_name_available_utils(name=medicine_master.medicine_name, table=MedicineMasterModel, field="medicine_name", db=db)
        if check_medicine_name_exists != "unique":
            raise HTTPException(status_code=400, detail="Medicine already exists")
        
        new_medicine_master_bl = MedicineMasterModel(
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
            active_flag = 1,
            composition = medicine_master.composition
        )
        # this will hold a data of a created medicine
        medicine_master_created_data = create_medicine_master_dal(new_medicine_master_bl, db)
        return MedicineMasterMessage(message="Medicine Master Created successfully") #medicine_master_created_data
    except Exception as e:
        logger.error(f"Database error in creating medicine master BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating medicine master BL: " + str(e))

def get_medicine_list_bl(db:Session):
    """
    Get Medicine list by active_flag=1
    """
    try:
        medicines = get_medicine_list_dal(db)
        medicines_list = []
        for medicine in medicines:
            medicine_data = {
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "generic_name": medicine.generic_name,
                "hsn_code": medicine.hsn_code,
                "formulation": medicine.formulation,
                "strength": medicine.strength,
                "unit_of_measure": medicine.unit_of_measure,
                "manufacturer_id": medicine.manufacturer_id,
                "category_id": medicine.category_id,
                "composition": medicine.composition,
                "created_at": medicine.created_at,
                "updated_at": medicine.updated_at,
                "active_flag": medicine.active_flag 
            }
            medicines_list.append(medicine_data)
        return medicines_list
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in fetching list of medicine master BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching list of medicine master BL: " + str(e))

def get_medicine_master_bl(medicine_name: str, db: Session):
    
    """
    Get medicine_master  by medicine_name
    """
    try:
        check_medicine_name_exists = check_name_available_utils(name=medicine_name, table=MedicineMasterModel, field="medicine_name", db=db)
        if check_medicine_name_exists=="unique":
            raise HTTPException(status_code=400, detail="Medicine Not found")
        medicine_master = get_medicine_master_dal(medicine_name, db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error in fetch medicine master BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetch medicine master BL: " + str(e))

def update_medicine_master_bl(medicine_name: str, medicine_master: UpdateMedicine, db: Session):
    """
    Update medicine_master  by medicine_name
    """
    try:
        # Validate by medicine_name
        check_medicine_name_exists = check_name_available_utils(name=medicine_name, table=MedicineMasterModel, field="medicine_name", db=db)
        if check_medicine_name_exists == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        
        # Validate category_id
        if not check_name_available_utils(name=medicine_master.category_id, table=MedicineMasterModel, field="category_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid category_id")

        # Validate manufacturer_id
        if not check_name_available_utils(name=medicine_master.manufacturer_id, table=MedicineMasterModel, field="manufacturer_id", db=db):
            raise HTTPException(status_code=400, detail="Invalid manufacturer_id")
        # this will have a updated medicine master 
        updated_medicine_master = update_medicine_master_dal(medicine_name, medicine_master, db)
        return MedicineMasterMessage(message="Medicine updated Successfuly") #updated_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in updating the medicine master BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating the medicine master BL: " + str(e))

def activate_medicine_bl(medicine_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        check_medicine_name_exists = check_name_available_utils(name=medicine_name, table=MedicineMasterModel, field="medicine_name", db=db)
        if check_medicine_name_exists=="unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        # this will hold a medicine master activated or inactive data
        activate_inactive_medicine_master = activate_medicine_dal(medicine_name, active_flag, db)
        if active_flag==1:
            return MedicineMasterMessage(message="Medicine activated Successfuly")
        return MedicineMasterMessage(message="Medicine deactivated Successfuly")
          #activate_inactive_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activating or inactivate medicine BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activating or inactivate medicine BL: " + str(e))

        