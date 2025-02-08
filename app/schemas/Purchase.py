from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime

class DeletePurchase(BaseModel):
    """
    Model for delete purchase request
    """
    purchase_id:str
    
    class Config:
        from_attributes = True 
        
class PurchaseMessage(BaseModel):
    """
    Message for Pricing
    """
    message: str = Field(..., description="Message for Pricing")
    
    class Config:
        from_attributes = True