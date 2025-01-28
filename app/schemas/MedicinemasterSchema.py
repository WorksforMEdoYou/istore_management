from pydantic import BaseModel, constr
from typing import Optional

class MedicineMasterBase(BaseModel):
    
    """
    Base model for MedicineMaster containing common fields.
    """
    medicine_name: constr(max_length=255)
    generic_name: constr(max_length=255)
    hsn_code: constr(max_length=10)
    formulation: constr(max_length=50)
    strength: constr(max_length=50)
    unit_of_measure: constr(max_length=10)
    manufacturer_id: int
    category_id: int

class MedicineMasterCreate(MedicineMasterBase):
    
    """
    Pydantic model for creating a new medicine record.
    """
    pass

class MedicineMaster(MedicineMasterBase):
    
    """
    Pydantic model for representing detailed medicine information.
    """
    medicine_id: Optional[int]

    class Config:
        from_attributes = True