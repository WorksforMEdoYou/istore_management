from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.mysql_session import get_db
from ..models.store_mysql_models import Distributor as DistributorModel
from ..schemas.DistributorSchema import Distributor as DistributorSchema, DistributorCreate, UpdateDistributor, DistributorActivate, DistributorMessage
import logging
from typing import List
from ..Service.distributor import creating_distributor_bl, update_distributor_bl, get_distibutor_bl, get_distributors_list_bl, activate_distributor_bl

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/distributors/create/", response_model=DistributorMessage, status_code=status.HTTP_201_CREATED)
def create_distributor_endpoint(distributor: DistributorCreate, db: Session = Depends(get_db)):
    try:
        distributor_data = creating_distributor_bl(distributor=distributor, db=db)
        return distributor_data
    except SQLAlchemyError as e:
        logger.error(f"Database error in creating Distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating Distributor: " + str(e))

@router.get("/distributors/", response_model=list, status_code=status.HTTP_200_OK)
def list_distributors_endpoint(db: Session = Depends(get_db)):
    try:
        distributors_list = get_distributors_list_bl(db=db)
        return distributors_list
    except SQLAlchemyError as e:
        logger.error(f"Database error in fetching distributor list: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching distributor list: " + str(e))

@router.get("/distributors/{distributor_name}", response_model=DistributorSchema, status_code=status.HTTP_200_OK)
def get_distributor_endpoint(distributor_name: str, db: Session = Depends(get_db)):
    try:
        individual_distributor = get_distibutor_bl(distributor_name=distributor_name, db=db)
        return individual_distributor
    except SQLAlchemyError as e:
        logger.error(f"Database error in fetching distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching distributor: " + str(e))

@router.put("/distributors/update/", response_model=DistributorMessage, status_code=status.HTTP_200_OK)
def update_distributor_endpoint(distributor: UpdateDistributor, db: Session = Depends(get_db)):
    try:
        update_distributor = update_distributor_bl(distributor_name=distributor.distributor_name, distributor=distributor, db=db)
        return update_distributor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in updating distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating distributor: " + str(e))

@router.put("/distibutors/active/", response_model=DistributorMessage, status_code=status.HTTP_200_OK)
def update_distributor_active_status_endpoint(distributor:DistributorActivate, db: Session = Depends(get_db)):
    try:
        status_distributor = activate_distributor_bl(distributor_name=distributor.distributor_name, active_flag=distributor.active_flag, db=db)
        return status_distributor
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activating or inactive distributor: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activating or inactive distributor: " + str(e))
