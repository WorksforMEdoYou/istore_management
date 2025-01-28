from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from istore.app.db.mysql import get_db
from istore.app.models.store_mysql_models import Category as CategoryModel
from istore.app.schemas.CaregorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List
from istore.app.Service.category import creating_category_record, get_category_record, update_category_record, get_category_list, activate_category_record

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/categories/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        create_category = creating_category_record(category=category, db=db)
        return create_category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/", status_code=status.HTTP_200_OK)
def list_categories(db: Session = Depends(get_db)):
    try:
        categories = get_category_list(db=db)
        if categories:
            return categories
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.get("/categories/{category_name}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
def get_category(category_name: str, db: Session = Depends(get_db)):
    try:
        category = get_category_record(category_name=category_name, db=db)
        return category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/categories/{category_name}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
def update_category(category_name: str, category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        db_category = update_category_record(category_name=category_name, category=category, db=db)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/categories/active/{categories_name}", status_code=status.HTTP_200_OK)
def update_categories_active_status(categories_name: str, active_flag: int, db: Session = Depends(get_db)):
    try:
        db_categories = activate_category_record(category_name=categories_name, active_flag=active_flag, db=db)
        return db_categories
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))