from pydantic import BaseModel, constr
from typing import Optional

class CategoryBase(BaseModel):
    
    """
    Base model for Category containing common fields.
    """
    category_name: constr(max_length=255)

class CategoryCreate(CategoryBase):
    
    """
    Pydantic model for creating a new category record.
    """
    pass

class Category(CategoryBase):
    
    """
    Pydantic model for representing detailed Category information.
    """
    category_id: Optional[int]

    class Config:
        from_attributes = True