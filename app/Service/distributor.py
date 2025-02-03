from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import Distributor as DistributorModel
from ..schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate, UpdateDistributorRecord
import logging
from typing import List
from datetime import datetime
from ..utils import check_name_available
from ..crud.distributor import creating_distributor_record_db, get_all_distributors_db, get_distibutor_record_db, update_distributor_record_db, activate_distributor_record_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_distributor_record(distributor:DistributorCreate, db: Session):
    
    """
    Creating distributor record
    """
    try:
        verify_distributor = check_name_available(name = distributor.distributor_name, model=DistributorModel, field="distributor_name", db=db)
        if verify_distributor!="unique":
            raise HTTPException(status_code=400, detail="Distributor already exists")
        db_distributor = DistributorModel(
            distributor_name=distributor.distributor_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        distributor = creating_distributor_record_db(db_distributor, db)
        return distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_all_distributors(db:Session):
    """
    Get all distributors by active_flag=1
    """
    try:
        distributors_list = get_all_distributors_db(db)
        return distributors_list
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
  
def get_distibutor_record(distributor_name: str, db: Session):
    
    """
    Get distributor record by distributor_id
    """
    try:
        verify_distributor = check_name_available(name = distributor_name, model=DistributorModel, field="distributor_name", db=db)
        if verify_distributor=="unique":
            raise HTTPException(status_code=404, detail="Distributor not found")
        distributor = get_distibutor_record_db(distributor_name, db)
        return distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def map_distributor_to_update_distributor_record(distributor: DistributorModel, update_distributor_name: str) -> UpdateDistributorRecord:
    return UpdateDistributorRecord(
        distributor_name=distributor.distributor_name,
        update_distributor_name=update_distributor_name  # Use the provided update_distributor_name
    )

def update_distributor_record(distributor_name: str, distributor: UpdateDistributorRecord, db: Session):
    """
    Update distributor record by distributor_name
    """
    try:
        verify_distributor = check_name_available(name=distributor_name, model=DistributorModel, field="distributor_name", db=db)
        if verify_distributor == "unique":
            raise HTTPException(status_code=404, detail="Distributor not found")
        db_distributor = update_distributor_record_db(distributor_name, distributor, db)
        return map_distributor_to_update_distributor_record(db_distributor, distributor.update_distributor_name)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def activate_distributor_record(distributor_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        verify_distributor = check_name_available(name = distributor_name, model=DistributorModel, field="distributor_name", db=db)
        if verify_distributor=="unique":
            raise HTTPException(status_code=400, detail="Distributor not found")
        db_distributor = activate_distributor_record_db(distributor_name, active_flag, db)
        return db_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
