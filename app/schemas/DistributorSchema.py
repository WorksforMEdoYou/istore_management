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