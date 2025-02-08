from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from istore.app.db.mysql import get_db
from istore.app.models.store_mysql_models import Category as CategoryModel
from istore.app.schemas.CaregorySchema import Category as CategorySchema, CategoryCreate, UpdatingCategory, CategoryMessage, ActivateCategory
import logging
from typing import List
from istore.app.Service.category import creating_category_bl, get_category_bl, get_category_list_bl, update_category_bl, activate_category_bl

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/categories/create/", response_model=CategoryMessage, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        create_category_data = creating_category_bl(category=category, db=db)
        return create_category_data
    except Exception as e:
        logger.error(f"Database error in creating category record: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating category record: " + str(e))

@router.get("/categories/list/", status_code=status.HTTP_200_OK)
def list_categories_endpoint(db: Session = Depends(get_db)):
    try:
        categories_list = get_category_list_bl(db=db)
        if categories_list:
            return categories_list
    except Exception as e:
        logger.error(f"Database error in fetching list of category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching list of category: " + str(e))

@router.get("/categories/{category_name}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
def get_category_endpoint(category_name: str, db: Session = Depends(get_db)):
    try:
        category = get_category_bl(category_name=category_name, db=db)
        return category
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.put("/categories/", response_model=CategoryMessage, status_code=status.HTTP_200_OK)
def update_category_endpoint(category: UpdatingCategory, db: Session = Depends(get_db)):
    try:
        updated_category = update_category_bl(category_name=category.category_name, update_category=category.update_category_name, db=db)
        return updated_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in updating category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating category: " + str(e))

@router.put("/categories/active/", response_model=CategoryMessage, status_code=status.HTTP_200_OK)
def update_categories_active_status_endpoint(activate: ActivateCategory, db: Session = Depends(get_db)):
    try:
        activating_categories = activate_category_bl(category_name=activate.category_name, active_flag=activate.active_flag, db=db)
        return activating_categories
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activating or deactivating category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activating or deactivating category: " + str(e))