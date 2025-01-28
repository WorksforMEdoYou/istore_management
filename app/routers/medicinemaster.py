from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from ..schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate
import logging
from ..Service.medicine_master import create_medicine_master_record, get_medicine_master_record, update_medicine_master_record, get_medicine_list, activate_medicine_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_master/", response_model=MedicineMasterSchema, status_code=status.HTTP_201_CREATED)
def create_medicine_master(medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        db_medicine_master = create_medicine_master_record(medicine_master=medicine_master, db=db)
        return db_medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/", status_code=status.HTTP_200_OK)
def get_all_medicine_master(db: Session = Depends(get_db)):
    try:
        medicine_master = get_medicine_list(db=db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/medicine_master/{medicine_name}", response_model=MedicineMasterSchema, status_code=status.HTTP_200_OK)
def get_medicine_master(medicine_name: str, db: Session = Depends(get_db)):
    try:
        medicine_master = get_medicine_master_record(medicine_name=medicine_name, db=db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_master/{medicine_name}", response_model=MedicineMasterSchema, status_code=status.HTTP_200_OK)
def update_medicine_master(medicine_name: str, medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        db_medicine_master = update_medicine_master_record(medicine_name=medicine_name, medicine_master=medicine_master, db=db)
        return db_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/medicine_master/activate/{medicine_name}", status_code=status.HTTP_200_OK)
def activate_deactivate(medicine_name:str, active_flag:int, db:Session = Depends(get_db)):
    try:
        db_medicine = activate_medicine_record(medicine_name=medicine_name, active_flag=active_flag, db=db)
        return db_medicine
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))