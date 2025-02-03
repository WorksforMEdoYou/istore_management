from pydantic import BaseModel, constr
from typing import Optional

class DistributorBase(BaseModel):
    
    """
    Base model for Distributor containing common fields.
    """
    distributor_name: constr(max_length=255)

class DistributorCreate(DistributorBase):
    
    """
    Pydantic model for creating a new distributor record.
    """
    pass

class Distributor(DistributorBase):
    
    """
    Pydantic model for representing detailed distributor information.
    """
    distributor_id: Optional[int]

    class Config:
        from_attributes = True
        
class UpdateDistributorRecord(DistributorBase):
    """
    Pydantic model for updating an existing distributor record.
    """
    update_distributor_name: str
    
    class Config:
        from_attributes = True
        
class DistributorActivate(BaseModel):
    """
    Pydantic model for activating a distributor record.
    """
    distributor_name: str
    active_flag: int
    
    class Config:
        from_attributes = True