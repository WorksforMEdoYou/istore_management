from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.store_mysql_models import Distributor as DistributorModel
from ..schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate, UpdateDistributor, DistributorMessage
import logging
from typing import List
from datetime import datetime
from ..utils import check_name_available_utils
from ..crud.distributor import creating_distributor_dal, update_distributor_dal, get_all_distributors_dal, get_distibutor_dal, activate_distributor_dal

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_distributor_bl(distributor:DistributorCreate, db: Session):
    
    """
    Creating distributor  BL
    """
    try:
        check_distributor_exists = check_name_available_utils(name = distributor.distributor_name, table=DistributorModel, field="distributor_name", db=db)
        if check_distributor_exists!="unique":
            raise HTTPException(status_code=400, detail="Distributor already exists")
        new_distributor_data_bl = DistributorModel(
            distributor_name=distributor.distributor_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        # this variable will hold all the value of the created distributor
        created_distributor = creating_distributor_dal(new_distributor_data_bl, db)
        return DistributorMessage(message="Distributor Created Successfully") #created_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error in creating the distributor BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the distributor BL: " + str(e))

def get_distributors_list_bl(db:Session):
    """
    Get all distributors by active_flag=1
    """
    try:
        distributors = get_all_distributors_dal(db)
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
        logger.error(f"Database error in fetching list of distributors BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching list of distributors BL: " + str(e))
  
def get_distibutor_bl(distributor_name: str, db: Session):
    
    """
    Get distributor  by distributor_name
    """
    try:
        verify_distributor = check_name_available_utils(name = distributor_name, table=DistributorModel, field="distributor_name", db=db)
        if verify_distributor=="unique":
            raise HTTPException(status_code=404, detail="Distributor not found")
        individual_distributor = get_distibutor_dal(distributor_name, db)
        return individual_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error in fetching distributor BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching distributor BL: " + str(e))
    
def update_distributor_bl(distributor_name: str, distributor: UpdateDistributor, db: Session):
    """
    Update distributor  by distributor_name
    """
    try:
        check_distributor_exist = check_name_available_utils(name=distributor_name, table=DistributorModel, field="distributor_name", db=db)
        if check_distributor_exist == "unique":
            raise HTTPException(status_code=404, detail="Distributor not found")
        db_distributor = update_distributor_dal(distributor_name, distributor, db)
        return DistributorMessage(message="Distributor Updated successfully") #db_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in updating distributor BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating distributor BL: " + str(e))

def activate_distributor_bl(distributor_name, active_flag, db:Session):
    """
    Updating the distributor active flag 0 or 1
    """
    try:
        check_distributor_exist = check_name_available_utils(name = distributor_name, table=DistributorModel, field="distributor_name", db=db)
        if check_distributor_exist=="unique":
            raise HTTPException(status_code=400, detail="Distributor not found")
        # this will hold a activated or deleted distributor
        activated_inactivated_distributor_data = activate_distributor_dal(distributor_name, active_flag, db)
        if active_flag==1:
            return  DistributorMessage(message="Distributor activated Successfully")
        if active_flag==0:
            return DistributorMessage(message="Distributor inactivated Successfully") #activated_inactivated_distributor_data
    except Exception as e:
        db.rollback()
        logger.error(f"Database error BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error BL: " + str(e))
