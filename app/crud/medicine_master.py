from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from ..schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate, UpdateMedicine
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_medicine_master_record_db(db_medicine_master, db: Session):
    """
    Creating medicine_master record
    """
    try:
        db.add(db_medicine_master)
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_list_db(db:Session):
    """
    Get Medicine list by active_flag=1
    """
    try:
        medicines = db.query(MedicineMasterModel).filter(MedicineMasterModel.active_flag == 1).all()
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
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_medicine_master_record_db(medicine_name: str, db: Session):
    
    """
    Get medicine_master record by medicine_id
    """
    try:
        medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if medicine_master:
            return medicine_master
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def update_medicine_master_record_db(medicine_name: str, medicine_master: UpdateMedicine, db: Session):
    """
    Update medicine_master record by medicine_id
    """
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        db_medicine_master.medicine_name = medicine_master.medicine_name
        db_medicine_master.generic_name = medicine_master.generic_name
        db_medicine_master.hsn_code = medicine_master.hsn_code
        db_medicine_master.formulation = medicine_master.formulation
        db_medicine_master.strength = medicine_master.strength
        db_medicine_master.unit_of_measure = medicine_master.unit_of_measure
        db_medicine_master.manufacturer_id = medicine_master.manufacturer_id
        db_medicine_master.category_id = medicine_master.category_id
        db_medicine_master.composition = medicine_master.composition
        db_medicine_master.updated_at = datetime.now()
        
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def activate_medicine_record_db(medicine_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        db_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not db_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        db_medicine_master.active_flag = active_flag
        db_medicine_master.updated_at = datetime.now()
        db.commit()
        db.refresh(db_medicine_master)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

        