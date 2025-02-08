from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime

class DeleteOrder(BaseModel):
    """
    Delete Order Request Model
    """
    order_id: str = Field(..., title="Order ID", description="ID of the order")
    class Config:
        from_attributes = True
        
class OrderMessage(BaseModel):
    """
    message for Order
    """
    message: str = Field(..., title="Message", description="Message for Order")
    class Config:
        from_attributes = True
