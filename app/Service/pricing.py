from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
from ..schemas.Pricing import UpdatePricing
from ..models.store_mysql_models import StoreDetails, MedicineMaster
import logging
from ..utils import validate_by_id, discount
from datetime import datetime
from ..crud.pricing import create_pricing_collection_db, delete_pricing_collection_db, get_all_collection_db

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_pricing_collection(pricing: Pricing, db, mysql_db: Session):
    """
    Creating the pricing collection in the database.
    """
    try:
        pricing_dict = pricing.dict()
        # Validate store
        validate_store = validate_by_id(id=pricing_dict["store_id"], model=StoreDetails, field="store_id", db=mysql_db)
        if validate_store == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        validate_medicine = validate_by_id(id=pricing_dict["medicine_id"], model=MedicineMaster, field="medicine_id", db=mysql_db)
        if validate_medicine == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        # Discount medicine
        if pricing_dict["discount"] > 0:
            pricing = discount(mrp=pricing_dict["mrp"], discount=pricing_dict["discount"])
        else:
            pricing = pricing_dict["mrp"]
        result = {
            "store_id": pricing_dict["store_id"],
            "medicine_id": pricing_dict["medicine_id"],
            "price": pricing,  # discounted pricing
            "mrp": pricing_dict["mrp"],
            "discount": pricing_dict["discount"],
            "net_rate": pricing_dict["net_rate"],
            "is_active": pricing_dict["is_active"],
            "last_updated_by": pricing_dict["last_updated_by"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active_flag": 1
        }
        pricing_medicine = await create_pricing_collection_db(pricing=result, db=db)
        return pricing_medicine
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_all_collection(store_id: int, medicine_id: int, db, mysql_db: Session):
    """
    Getting all the pricing by store
    """
    try:
        # Validate store
        validate_store = validate_by_id(id=store_id, model=StoreDetails, field="store_id", db=mysql_db)
        if validate_store == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        validate_medicine = validate_by_id(id=medicine_id, model=MedicineMaster, field="medicine_id", db=mysql_db)
        if validate_medicine == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")

        result = await get_all_collection_db(store_id=store_id, medicine_id=medicine_id, db=db)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_pricing_collection(store_id: int, medicine_id: int, db, mysql_db: Session):
    """
    Deleting the pricing collection in the database.
    """
    try:
        # Validate store
        validate_store = validate_by_id(id=store_id, model=StoreDetails, field="store_id", db=mysql_db)
        if validate_store == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        validate_medicine = validate_by_id(id=medicine_id, model=MedicineMaster, field="medicine_id", db=mysql_db)
        if validate_medicine == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")

        delete_result = await delete_pricing_collection_db(store_id=store_id, medicine_id=medicine_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))