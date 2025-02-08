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

def create_medicine_master_dal(new_medicine_master_dal, db: Session):
    """
    Creating medicine_master DAL
    """
    try:
        db.add(new_medicine_master_dal)
        db.commit()
        db.refresh(new_medicine_master_dal)
        return new_medicine_master_dal
    except Exception as e:
        logger.error(f"Database error while creating the medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the medicine master: " + str(e))

def get_medicine_list_dal(db:Session):
    """
    Get Medicine list by active_flag=1
    """
    try:
        medicines_list = db.query(MedicineMasterModel).filter(MedicineMasterModel.active_flag == 1).all()
        if medicines_list:
            return medicines_list
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while fetching list of medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching list of medicine master: " + str(e))

def get_medicine_master_dal(medicine_name: str, db: Session):
    
    """
    Get medicine_master by medicine_name
    """
    try:
        medicine_master_individual = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if medicine_master_individual:
            return medicine_master_individual
        raise HTTPException(status_code=404, detail="Medicine not found")
    except Exception as e:
        logger.error(f"Database error while fetching medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching medicine master: " + str(e))

def update_medicine_master_dal(medicine_name: str, medicine_master: UpdateMedicine, db: Session):
    """
    Update medicine_master by medicine_name
    """
    try:
        update_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not update_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        
        update_medicine_master.medicine_name = medicine_master.medicine_update_name
        update_medicine_master.generic_name = medicine_master.generic_name
        update_medicine_master.hsn_code = medicine_master.hsn_code
        update_medicine_master.formulation = medicine_master.formulation
        update_medicine_master.strength = medicine_master.strength
        update_medicine_master.unit_of_measure = medicine_master.unit_of_measure
        update_medicine_master.manufacturer_id = medicine_master.manufacturer_id
        update_medicine_master.category_id = medicine_master.category_id
        update_medicine_master.composition = medicine_master.composition
        update_medicine_master.updated_at = datetime.now()
        
        db.commit()
        db.refresh(update_medicine_master)
        return update_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while updating medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating medicine master: " + str(e))
    
def activate_medicine_dal(medicine_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        activate_inactivate_medicine_master = db.query(MedicineMasterModel).filter(MedicineMasterModel.medicine_name == medicine_name).first()
        if not activate_inactivate_medicine_master:
            raise HTTPException(status_code=404, detail="Medicine not found")
        activate_inactivate_medicine_master.active_flag = active_flag
        activate_inactivate_medicine_master.updated_at = datetime.now()
        db.commit()
        db.refresh(activate_inactivate_medicine_master)
        return activate_inactivate_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

        