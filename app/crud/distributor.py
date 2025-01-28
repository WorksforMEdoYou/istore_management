from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import Distributor as DistributorModel
from ..schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate
import logging
from typing import List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_distributor_record_db(db_distributor, db: Session):
    
    """
    Creating distributor record
    """
    try:
        db.add(db_distributor)
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_all_distributors_db(db:Session):
    """
    Get all distributors by active_flag=1
    """
    try:
        distributors = db.query(DistributorModel).filter(DistributorModel.active_flag == 1).all()
        distributors_list = []
        for distributor in distributors:
            distributor_data = {
                "distributor_id": distributor.distributor_id,
                "distributor_name": distributor.distributor_name,
                "created_at": distributor.created_at,
                "updated_at": distributor.updated_at,
                "active_flag": distributor.active_flag  
            }
            distributors_list.append(distributor_data)
        return distributors_list
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
  
def get_distibutor_record_db(distributor_name: str, db: Session):
    
    """
    Get distributor record by distributor_id
    """
    try:
        distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if distributor:
            return distributor
        else:
            raise HTTPException(status_code=404, detail="Distributor not found")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def update_distributor_record_db(distributor_name: str, distributor: DistributorCreate, db: Session):
    
    """
    Update distributor record by distributor_id
    """
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        db_distributor.distributor_name = distributor.distributor_name
        db_distributor.updated_at = datetime.now()
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def activate_distributor_record_db(distributor_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        db_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if not db_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        db_distributor.active_flag = active_flag
        db_distributor.updated_at = datetime.now()
        db.commit()
        db.refresh(db_distributor)
        return db_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
