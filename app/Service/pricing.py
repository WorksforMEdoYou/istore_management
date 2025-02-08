from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Pricing
from ..schemas.Pricing import UpdatePricing, PricingMessage
from ..models.store_mysql_models import StoreDetails, MedicineMaster
import logging
from ..utils import validate_by_id_utils, discount
from datetime import datetime
from ..crud.pricing import create_pricing_collection_dal, get_all_pricing_collection_dal, update_pricing_dal, delete_pricing_collection_dal

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_pricing_collection_bl(new_pricing_data_bl: Pricing, db, mysql_db: Session):
    """
    Creating the pricing collection in the database.
    """
    try:
        pricing_dict = new_pricing_data_bl.dict()
        # Validate store
        check_store_exists = validate_by_id_utils(id=pricing_dict["store_id"], table=StoreDetails, field="store_id", db=mysql_db)
        if check_store_exists == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        check_medicine_exists = validate_by_id_utils(id=pricing_dict["medicine_id"], table=MedicineMaster, field="medicine_id", db=mysql_db)
        if check_medicine_exists == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        # Discount medicine
        if pricing_dict["discount"] > 0:
            pricing = discount(mrp=pricing_dict["mrp"], discount=pricing_dict["discount"])
        else:
            pricing = pricing_dict["mrp"]
        create_pricing_data = {
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
        # this will hold all the data of created pricing
        pricing_medicine = await create_pricing_collection_dal(create_pricing_data, db)
        return PricingMessage(message="Pricing Created Successfully") #pricing_medicine
    except Exception as e:
        logger.error(f"Database error in creating pricing BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating pricing BL: " + str(e))

async def get_all_pricing_collection_list_bl(store_id: int, medicine_id: int, db, mysql_db: Session):
    """
    Getting all the pricing list by store
    """
    try:
        # Validate store
        validate_store = validate_by_id_utils(id=store_id, table=StoreDetails, field="store_id", db=mysql_db)
        if validate_store == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        validate_medicine = validate_by_id_utils(id=medicine_id, table=MedicineMaster, field="medicine_id", db=mysql_db)
        if validate_medicine == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")

        all_pricing_by_store = await get_all_pricing_collection_dal(store_id=store_id, medicine_id=medicine_id, db=db)
        return all_pricing_by_store
    except Exception as e:
        logger.error(f"Database error in fetching list of pricings BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching list of pricings BL: " + str(e))

async def update_pricing_logic_bl(pricing: UpdatePricing, db, mysql_db: Session):
    """
    Updating the pricing of the medicine
    """
    try:
        # Validate store
        check_store_exists = validate_by_id_utils(id=pricing.store_id, table=StoreDetails, field="store_id", db=mysql_db)
        if check_store_exists == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        check_medicine_exists = validate_by_id_utils(id=pricing.medicine_id, table=MedicineMaster, field="medicine_id", db=mysql_db)
        if check_medicine_exists == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        # Discount medicine
        if pricing.discount > 0:
            pricing_discount = discount(mrp=pricing.mrp, discount=pricing.discount)
        else:
            pricing_discount = pricing.mrp
        # this will hold all the updated data of pricing
        updated_pricing = await update_pricing_dal(pricing=pricing, pricing_discount=pricing_discount, db=db)
        return PricingMessage(message="Pricing Updated Successfully") #updated_pricing
    except Exception as e:
        logger.error(f"Database error in updating the pricing BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in updating the pricing BL: " + str(e))

async def delete_pricing_collection_bl(store_id: int, medicine_id: int, db, mysql_db: Session):
    """
    Deleting the pricing collection in the database.
    """
    try:
        # Validate store
        check_store_exists = validate_by_id_utils(id=store_id, table=StoreDetails, field="store_id", db=mysql_db)
        if check_store_exists == "unique":
            raise HTTPException(status_code=400, detail="Store not found")
        # Validate medicine
        check_medicine_exists = validate_by_id_utils(id=medicine_id, table=MedicineMaster, field="medicine_id", db=mysql_db)
        if check_store_exists == "unique":
            raise HTTPException(status_code=400, detail="Medicine not found")
        #this will hold all the data of the deleted store
        deleted_pricing = await delete_pricing_collection_dal(store_id=store_id, medicine_id=medicine_id, db=db)
        return PricingMessage(message="Pricing Deleted Successfully") #deleted_pricing
    except Exception as e:
        logger.error(f"Database error in delete pricing BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in delete pricing BL: " + str(e))