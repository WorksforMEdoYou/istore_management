from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from istore.app.models.store_mysql_models import Category as CategoryModel
from istore.app.schemas.CaregorySchema import Category as CategorySchema, CategoryCreate
import logging
from typing import List
from datetime import datetime
from istore.app.utils import check_name_available
from istore.app.crud.category import creating_category_record_db, get_category_list_db, get_category_record_db, update_category_record_db, activate_category_record_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_category_record(category:CategoryCreate, db: Session):
    
    """
    Creating category record
    """
    try:
        category_available = check_name_available(name = category.category_name, model=CategoryModel, field="category_name", db=db)
        if category_available!="unique":
            raise HTTPException(status_code=400, detail="Category already exists")
        db_category = CategoryModel(
            category_name = category.category_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        values = creating_category_record_db(db_category, db)
        return values
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while creating category record")

def get_category_list(db:Session):
    """
    Get list of all category
    """
    try:
        category_list = get_category_list_db(db)
        return category_list
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_category_record(category_name: str, db: Session):
    
    """
    Get category record by category_id    
    """
    try:
        category_available = check_name_available(name=category_name, model=CategoryModel, field="category_name", db=db)
        if category_available=="unique":
            raise HTTPException(status_code=400, detail="Category not found")
        category = get_category_record_db(category_name, db)
        if category:
            return category
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e)+ " while getting category record")
    
def update_category_record(category_name: str, category: CategoryCreate, db: Session):
    """
    Update category record by category_id
    """
    try:
        category_available = check_name_available(name=category_name, model=CategoryModel, field="category_name", db=db)
        if category_available == "unique":
            raise HTTPException(status_code=404, detail="Category not found")
        db_category = update_category_record_db(category_name=category_name, category=category, db=db)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e) + " while updating category record")
    
def activate_category_record(category_name:str, active_flag:int, db:Session):
    """
    Updating the category active flag 0 or 1
    """
    try:
        category_available = check_name_available(name=category_name, model=CategoryModel, field="category_name", db=db)
        if category_available=="unique":
            raise HTTPException(status_code=404, detail="Category not found")
        db_category = activate_category_record_db(category_name=category_name, active_flag=active_flag, db=db)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
