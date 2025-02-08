from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from istore.app.models.store_mysql_models import Category as CategoryModel
from istore.app.schemas.CaregorySchema import Category as CategorySchema, CategoryCreate, CategoryMessage
import logging
from typing import List
from datetime import datetime
from istore.app.utils import check_name_available_utils
from istore.app.crud.category import creating_category_dal, get_category_list_dal, get_single_category_dal, update_category_dal, activate_category_dal

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def creating_category_bl(category:CategoryCreate, db: Session):
    
    """
    Creating category 
    """
    try:
        category_available = check_name_available_utils(name = category.category_name, table=CategoryModel, field="category_name", db=db)
        if category_available!="unique":
            raise HTTPException(status_code=400, detail="Category already exists")
        db_category = CategoryModel(
            category_name = category.category_name,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            active_flag = 1
        )
        # this will hold all the values from the created category
        created_category_data = creating_category_dal(db_category, db)
        return CategoryMessage(message="Category Created Successfully")  #created_category_data
    except Exception as e:
        logger.error(f"Database error in creating the category record BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the category record BL: " + str(e)+ " while creating category record")

def get_category_list_bl(db:Session):
    """
    Get list of all category
    """
    try:
        category_list = get_category_list_dal(db)
        category_list_data = []
        for category in category_list:
            category_data = {
                "category_id": category.category_id,
                "category_name": category.category_name,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "active_flag": category.active_flag
            }
            category_list_data.append(category_data)
        return category_list
    except Exception as e:
        logger.error(f"Database error in fetching list of category BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching list of category BL: " + str(e))

def get_category_bl(category_name: str, db: Session):
    
    """
    Get category  by category_id    
    """
    try:
        check_category_exist = check_name_available_utils(name=category_name, table=CategoryModel, field="category_name", db=db)
        if check_category_exist=="unique":
            raise HTTPException(status_code=400, detail="Category not found")
        single_category = get_single_category_dal(category_name, db)
        if single_category:
            return single_category
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        logger.error(f"Database error in fetching the single category record: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching the single category record: " + str(e)+ " while getting category record")
    
def update_category_bl(category_name: str, update_category: str, db: Session):
    """
    Update category by category_id
    """
    try:
        check_category_exist = check_name_available_utils(name=category_name, table=CategoryModel, field="category_name", db=db)
        if check_category_exist == "unique":
            raise HTTPException(status_code=404, detail="Category not found")
        # this will hold all the updated category
        updated_category = update_category_dal(category_name=category_name, update_category=update_category, db=db)
        return CategoryMessage(message="Category updated successfully") #updated_category
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while updating the category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error while updating the category: " + str(e) + " while updating category record")
       
def activate_category_bl(category_name: str, active_flag: int, db: Session):
    """
    Updating the category active flag 0 or 1
    """
    try:
        check_category_exists = check_name_available_utils(name=category_name, table=CategoryModel, field="category_name", db=db)
        if check_category_exists == "unique":
            raise HTTPException(status_code=404, detail="Category not found")
        activated_category = activate_category_dal(category_name=category_name, active_flag=active_flag, db=db)
        if active_flag == 1:
            return CategoryMessage(message="Category activated successfully")
        else:
            return CategoryMessage(message="Category deactivated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in activating category: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in activating category: " + str(e))
