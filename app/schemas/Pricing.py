from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime
from ..models.store_mongodb_models import Pricing

class UpdatePricing(Pricing):
    """
    Model for delete purchase request
    """
    pass   
        
class DeletePricing(BaseModel):
    """
    Model for delete purchase request
    """
    store_id: int = Field(..., description="store id for delete")
    medicine_id: int = Field(..., description="medicine id for the delete")
    
    class Config:
        from_attributes = True

class PricingMessage(BaseModel):
    """
    Message for the pricing
    """
    message: str = Field(..., description="message for the pricing")
    class Config:
        from_attributes = True
        