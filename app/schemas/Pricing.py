from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime
from ..models.store_mongodb_models import Pricing

class UpdatePricing(Pricing):
    """
    Model for delete purchase request
    """
    update_store_id: int = Field(..., description="updating purpose")
    update_medicine_id: int = Field(..., description="updating user id")
    
    class Config:
        from_attributes = True    
        
class DeletePricing(BaseModel):
    """
    Model for delete purchase request
    """
    store_id: int = Field(..., description="store id for delete")
    medicine_id: int = Field(..., description="medicine id for the delete")
    
    class Config:
        from_attributes = True
        