from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime

class DeleteSale(BaseModel):
    """
    Model for delete purchase request
    """
    sale_id:str
    
    class Config:
        from_attributes = True    