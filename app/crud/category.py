from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from istore.app.models.store_mysql_models import Category as CategoryModel
from istore.app.schemas.CaregorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_category_dal(creating_category_dal, db: Session):
    
    """
    Creating category 
    """
    try:
        db.add(creating_category_dal)
        db.commit()
        db.refresh(creating_category_dal)
        return creating_category_dal
    except Exception as e:
        logger.error(f"Database error while creating the caregory: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while creating the caregory: " + str(e)+ " while creating category record")

def get_category_list_dal(db:Session):
    """
    Get list of all category
    """
    try:
        list_categorys = db.query(CategoryModel).filter(CategoryModel.active_flag == 1).all()
        return list_categorys
    except Exception as e:
        logger.error(f"Database error while fetching list of category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching list of category: " + str(e))

def get_single_category_dal(category_name: str, db: Session):
    
    """
    Get category by category_id    
    """
    try:
        single_category_data = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if single_category_data:
            return single_category_data
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error while fetching single category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while fetching single category: " + str(e)+ " while getting category record")
    
def update_category_dal(category_name: str, update_category: str, db: Session):
    """
    Update category by category_name
    """
    try:
        updating_category = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if not updating_category:
            raise HTTPException(status_code=404, detail="Category not found")
        updating_category.category_name = update_category
        updating_category.updated_at = datetime.now()
        db.commit()
        db.refresh(updating_category)
        return updating_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while updating the category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating the category: " + str(e) + " while updating category record")

def activate_category_dal(category_name: str, active_flag: int, db: Session):
    """
    Updating the category active flag 0 or 1
    """
    try:
        activating_category = db.query(CategoryModel).filter(CategoryModel.category_name == category_name).first()
        if not activating_category:
            raise HTTPException(status_code=404, detail="Category not found")
        activating_category.active_flag = active_flag
        activating_category.updated_at = datetime.now()
        db.commit()
        db.refresh(activating_category)
        return activating_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while activating the category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while activating the category: " + str(e))