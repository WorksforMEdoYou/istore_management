from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime

class DeleteStock(BaseModel):
    """
    Delete stock request model
    """
    store_id: int = Field(..., description="store id for soft delete")
    medicine_id: int = Field(..., description="medicine id for soft delete")
    class Config:
        from_attributes = True 