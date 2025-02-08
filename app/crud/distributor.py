from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import Distributor as DistributorModel
from ..schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate, UpdateDistributor
import logging
from typing import List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_distributor_dal(new_distributor_data_dal, db: Session):
    
    """
    Creating distributor In Database
    """
    try:
        db.add(new_distributor_data_dal)
        db.commit()
        db.refresh(new_distributor_data_dal)
        return new_distributor_data_dal
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating the Distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the Distributor: " + str(e))

def get_all_distributors_dal(db:Session):
    """
    Get all distributors by active_flag=1
    """
    try:
        distributors_list = db.query(DistributorModel).filter(DistributorModel.active_flag == 1).all()
        if distributors_list:
            return distributors_list
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching the list of distributors: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching the list of distributors: " + str(e))
  
def get_distibutor_dal(distributor_name: str, db: Session):
    
    """
    Get distributor by distributor_id
    """
    try:
        distributor_data = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if distributor_data:
            return distributor_data
        else:
            raise HTTPException(status_code=404, detail="Distributor not found")
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching distributor: " + str(e))
    
def update_distributor_dal(distributor_name: str, distributor: UpdateDistributor, db: Session):
    """
    Update distributor by distributor_name
    """
    try:
        update_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if not update_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        update_distributor.distributor_name = distributor.update_distributor_name
        update_distributor.updated_at = datetime.now()
        db.commit()
        db.refresh(update_distributor)
        return update_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating distributor: " + str(e))

def activate_distributor_dal(distributor_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        activate_distributor = db.query(DistributorModel).filter(DistributorModel.distributor_name == distributor_name).first()
        if not activate_distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")
        activate_distributor.active_flag = active_flag
        activate_distributor.updated_at = datetime.now()
        db.commit()
        db.refresh(activate_distributor)
        return activate_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while activating distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while activating distributor: " + str(e))
