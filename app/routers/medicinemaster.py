from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster as MedicineMasterModel 
from ..schemas.MedicinemasterSchema import MedicineMaster as MedicineMasterSchema, MedicineMasterCreate, ActivateMedicine, UpdateMedicine, MedicineMasterMessage
import logging
from ..Service.medicine_master import create_medicine_master_bl, get_medicine_list_bl, get_medicine_master_bl, update_medicine_master_bl, activate_medicine_bl

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/medicine_master/create/", response_model=MedicineMasterMessage, status_code=status.HTTP_201_CREATED)
def create_medicine_master_endpoint(medicine_master: MedicineMasterCreate, db: Session = Depends(get_db)):
    try:
        medicine_master_data = create_medicine_master_bl(medicine_master=medicine_master, db=db)
        return medicine_master_data
    except Exception as e:
        logger.error(f"Database error in creating medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating medicine master: " + str(e))

@router.get("/medicine_master/", status_code=status.HTTP_200_OK)
def get_all_medicine_master_endpoint(db: Session = Depends(get_db)):
    try:
        medicine_master_list = get_medicine_list_bl(db=db)
        return medicine_master_list
    except Exception as e:
        logger.error(f"Database error in fetching lisst of medicines: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching lisst of medicines: " + str(e))

@router.get("/medicine_master/{medicine_name}", response_model=MedicineMasterSchema, status_code=status.HTTP_200_OK)
def get_medicine_master_endpoint(medicine_name: str, db: Session = Depends(get_db)):
    try:
        medicine_master = get_medicine_master_bl(medicine_name=medicine_name, db=db)
        return medicine_master
    except Exception as e:
        logger.error(f"Database error in fetching individual medicine master data: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching individual medicine master data: " + str(e))

@router.put("/medicine_master/", response_model=MedicineMasterMessage, status_code=status.HTTP_200_OK)
def update_medicine_master_endpoint(medicine: UpdateMedicine, db: Session = Depends(get_db)):
    try:
        updating_medicine_master = update_medicine_master_bl(medicine_name=medicine.medicine_update_name, medicine_master=medicine, db=db)
        return updating_medicine_master
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in updating medicine master: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating medicine master: " + str(e))

@router.put("/medicine_master/activate/", response_model=MedicineMasterMessage, status_code=status.HTTP_200_OK)
def activate_deactivate_endpoint(medicine:ActivateMedicine, db:Session = Depends(get_db)):
    try:
        activate_inactive_medicine = activate_medicine_bl(medicine_name=medicine.medicine_name, active_flag=medicine.active_flag, db=db)
        return activate_inactive_medicine
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activive or inactive medicine: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activive or inactive medicine: " + str(e))