from pydantic import BaseModel, constr
from typing import Optional
from enum import Enum

class StoreStatus(str, Enum):
    
    """
    Enum for the StoreStatus
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    
class StoreDetailsBase(BaseModel):
    
    """
    Base model for StoreDetails containing common fields.
    """
    store_name: constr(max_length=255)
    license_number: constr(max_length=50)
    gst_state_code: constr(max_length=2)
    gst_number: constr(max_length=50)
    pan: constr(max_length=10)
    address: str
    email: constr(max_length=100)
    mobile: constr(max_length=15)
    owner_name: constr(max_length=255)
    is_main_store: bool
    latitude: float
    longitude: float
    status: StoreStatus  # the store status can be active, inactive or closed

class StoreDetailsCreate(StoreDetailsBase):
    
    """
    Pydantic model for creating a new store details record.
    """
    pass

class StoreDetails(StoreDetailsBase):
    
    """
    Pydantic model for representing detailed storeDetails information.
    """
    store_id: Optional[int]

    class Config:
        from_attributes = True
        

class StoreSuspendActivate(BaseModel):
    """
    Pydantic model for suspending or activating a store.
    """
    
    remarks: str
    active_flag: int
    
    class Config:
        from_attributes = True