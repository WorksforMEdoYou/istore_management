from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from sqlalchemy.orm import Session
from ..db.mysql_session import get_db
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Purchase
import logging
from ..crud.purchase import create_purchase_collection_dal, get_all_purchases_list_dal, get_purchases_by_date_dal, get_purchases_by_id_dal, delete_purchase_collection_dal
from ..utils import validate_by_id_utils
from ..models.store_mysql_models import MedicineMaster, Distributor, Manufacturer, StoreDetails
from datetime import datetime
from ..utils import get_name_by_id_utils, validate_by_id_utils
from ..schemas.Purchase import PurchaseMessage

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_purchase_collection_bl(new_purchase_data_bl: Purchase, db, mysql_db: Session):
    """
    Creating the purchase collection.
    """
    try:
        purchase_dict = new_purchase_data_bl.model_dump(by_alias=True)
        # Distributor validation
        distributor_validation = validate_by_id_utils(id=new_purchase_data_bl.distributor_id, table=Distributor, field="distributor_id", db=mysql_db)
        if distributor_validation == "unique":
            raise HTTPException(status_code=404, detail="Distributor not Found.")
        
        purchase_items = []
        for item in new_purchase_data_bl.purchase_items:
            # medicine validation
            medicine_id = item.medicine_id
            if validate_by_id_utils(id=medicine_id, table=MedicineMaster, field="medicine_id", db=mysql_db) == "unique":
                raise HTTPException(status_code=404, detail="Medicine not found")
            # manufacturer validation
            manufacturer_id = item.manufacture_id
            if validate_by_id_utils(id=manufacturer_id, table=MedicineMaster, field="manufacturer_id", db=mysql_db) == "unique":
                raise HTTPException(status_code=404, detail="Manufacturer not found")
            
            # stock
            stock = {
                "expiry_date": item.expiry_date,
                "units_in_pack": item.packagetype_quantity,
                "batch": item.purchase_quantity,
                "batch_number": item.batch_number,
                "is_active": 1
            }
            # Update stock in the database
            await db.stocks.update_one(
                {"store_id": new_purchase_data_bl.store_id, "medicine_id": medicine_id},
                {
                    "$push": {"batch_details": stock},
                    "$inc": {"available_stock": item.purchase_quantity},
                    "$set": {"updated_at": datetime.now()}
                },
                upsert=True
            )
            logger.info("Updated in stocks")
            
            purchase_items.append({
                "medicine_id": medicine_id,
                "batch_number": item.batch_number,
                "expiry_date": item.expiry_date,
                "manufacture_id": item.manufacture_id,
                "medicine_form": item.medicine_form,
                "package_type": item.package_type,
                "units_per_package_type": item.units_per_package_type,
                "packagetype_quantity": item.packagetype_quantity,
                "purchase_mrp": item.purchase_mrp,
                "purchase_discount": item.purchase_discount,
                "purchase_amount": item.purchase_amount,
                "purchase_quantity": item.purchase_quantity
            })
        
        create_pricing = {
            "store_id": new_purchase_data_bl.store_id,
            "purchase_date": new_purchase_data_bl.purchase_date,
            "distributor_id": new_purchase_data_bl.distributor_id,
            "purchased_amount": new_purchase_data_bl.purchased_amount,
            "invoice_number": new_purchase_data_bl.invoice_number,  # Corrected field name
            "discount": new_purchase_data_bl.discount,
            "mrp": new_purchase_data_bl.mrp,
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
            "active_flag": 1,
            "purchase_items": purchase_items
        }
        # this will hold all the created pricing
        purchase_collection = await create_purchase_collection_dal(create_pricing, db=db)
        return PurchaseMessage(message="Purchase Created Successfully") #purchase_collection
    except Exception as e:
        logger.error(f"Database error in creating the pricing BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in creating the pricing BL: " + str(e))

async def get_all_purchase_list_bl(store_id: int, db, mysql_db: Session):
    """
    Get all purchases
    """
    try:
        purchases_by_store=[]
        purchased_list = await get_all_purchases_list_dal(store_id, db)
        async for purchase in purchased_list:
            purchase_id = str(purchase["_id"])
            purchase_date = str(purchase["purchase_date"])

            distributor_name = get_name_by_id_utils(id=purchase["distributor_id"], table=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            if distributor_name == "unique":
                raise HTTPException(status_code=400, detail="Distributor not Found")

            store_name = get_name_by_id_utils(id=purchase["store_id"], table=StoreDetails, field="store_id", name_field="store_name", db=mysql_db)
            if store_name == "unique":
                raise HTTPException(status_code=400, detail="Store not Found")
            total_amount = str(purchase["purchased_amount"])

            purchase_items = []
            for item in purchase["purchase_items"]:
                medicine_name = get_name_by_id_utils(id=item["medicine_id"], table=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
                if medicine_name == "unique":
                    raise HTTPException(status_code=400, detail="Medicine not Found")

                manufacturer_name = get_name_by_id_utils(id=item["manufacture_id"], table=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
                if manufacturer_name == "unique":
                    raise HTTPException(status_code=400, detail="Manufacturer not Found")

                purchase_items.append({
                    "medicine_id": item["medicine_id"],
                    "medicine_name": medicine_name,
                    "batch_number": item["batch_number"],
                    "quantity": item["purchase_quantity"],
                    "price": item["purchase_mrp"],
                    "expiry_date": item["expiry_date"],
                    "manufacturer_name": manufacturer_name,
                    "medicine_form": item["medicine_form"],
                    "units_in_pack": item["units_per_package_type"],
                    "unit_quantity": item["packagetype_quantity"],
                    "package": item["package_type"],
                    "package_count": item["packagetype_quantity"],
                    "medicine_quantity": item["purchase_quantity"]
                })

            purchases_by_store.append({
                "purchase_id": purchase_id,
                "store_id": purchase["store_id"],
                "store_name": store_name,
                "purchase_date": purchase_date,
                "distributor_id": purchase["distributor_id"],
                "distributor_name": distributor_name,
                "purchased_amount": total_amount,
                "invoice_number": purchase["invoice_number"],
                "purchase_items": purchase_items
            })
        return purchases_by_store
    except Exception as e:
        logger.error(f"Database error in fetching purchases list BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching purchases list BL: " + str(e))

async def get_purchase_collection_by_id_bl(purchase_id: str, db, mysql_db:Session):
    """
    Getting the purchase collection by id from the database.
    """
    try:
        single_purchase=[]
        purchase = await get_purchases_by_id_dal(id=purchase_id, db=db)
        purchase_id = str(purchase["_id"])
        purchase_date = str(purchase["purchase_date"])

        distributor_name = get_name_by_id_utils(id=purchase["distributor_id"], table=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
        if distributor_name == "unique":
            raise HTTPException(status_code=400, detail="Distributor not Found")

        store_name = get_name_by_id_utils(id=purchase["store_id"], table=StoreDetails, field="store_id", name_field="store_name", db=mysql_db)
        if store_name == "unique":
            raise HTTPException(status_code=400, detail="Store not Found")
            
        total_amount = str(purchase["purchased_amount"])

        purchase_items = []
        for item in purchase["purchase_items"]:
            medicine_name = get_name_by_id_utils(id=item["medicine_id"], table=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
            if medicine_name == "unique":
                raise HTTPException(status_code=400, detail="Medicine not Found")

            manufacturer_name = get_name_by_id_utils(id=item["manufacture_id"], table=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
            if manufacturer_name == "unique":
                raise HTTPException(status_code=400, detail="Manufacturer not Found")

            purchase_items.append({
                "medicine_id": item["medicine_id"],
                "medicine_name": medicine_name,
                "batch_number": item["batch_number"],
                "quantity": item["purchase_quantity"],
                "price": item["purchase_mrp"],
                "expiry_date": item["expiry_date"],
                "manufacturer_name": manufacturer_name,
                "medicine_form": item["medicine_form"],
                "units_in_pack": item["units_per_package_type"],
                "unit_quantity": item["packagetype_quantity"],
                "package": item["package_type"],
                "package_count": item["packagetype_quantity"],
                "medicine_quantity": item["purchase_quantity"]
            })

            single_purchase.append({
                "purchase_id": purchase_id,
                "store_id": purchase["store_id"],
                "store_name": store_name,
                "purchase_date": purchase_date,
                "distributor_id": purchase["distributor_id"],
                "distributor_name": distributor_name,
                "purchased_amount": total_amount,
                "invoice_number": purchase["invoice_number"],
                "purchase_items": purchase_items
            })
        return single_purchase
    except Exception as e:
        logger.error(f"Database error in fetching purchases by id BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching purchases by id BL: " + str(e))
    
async def get_purchases_by_date_store_bl(store_id:int, db, mysql_db:Session, start_date:str=None, end_date:str=None):
    """
    Get all purchases by date and store
    """
    try:
        purchases_by_store_date = []
        purchases_cursor = await get_purchases_by_date_dal(store_id=store_id, db=db, start_date=start_date, end_date=end_date)
        purchases = await purchases_cursor.to_list(length=None)
        for purchase in purchases:
            purchase_id = str(purchase["_id"])
            purchase_date = str(purchase["purchase_date"])

            distributor_name = get_name_by_id_utils(id=purchase["distributor_id"], table=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            if distributor_name == "unique":
                raise HTTPException(status_code=400, detail="Distributor not Found")

            store_name = get_name_by_id_utils(id=purchase["store_id"], table=StoreDetails, field="store_id", name_field="store_name", db=mysql_db) 
            if store_name == "unique":
                raise HTTPException(status_code=400, detail="Store not Found")
            
            total_amount = str(purchase["purchased_amount"])

            purchase_items = []
            for item in purchase["purchase_items"]:
                medicine_name = get_name_by_id_utils(id=item["medicine_id"], table=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
                if medicine_name == "unique":
                    raise HTTPException(status_code=400, detail="Medicine not Found")

                manufacturer_name = get_name_by_id_utils(id=item["manufacture_id"], table=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
                if manufacturer_name == "unique":
                    raise HTTPException(status_code=400, detail="Manufacturer not Found")

                purchase_items.append({
                    "medicine_id": item["medicine_id"],
                    "medicine_name": medicine_name,
                    "batch_number": item["batch_number"],
                    "quantity": item["purchase_quantity"],
                    "price": item["purchase_mrp"],
                    "expiry_date": item["expiry_date"],
                    "manufacturer_name": manufacturer_name,
                    "medicine_form": item["medicine_form"],
                    "units_in_pack": item["units_per_package_type"],
                    "unit_quantity": item["packagetype_quantity"],
                    "package": item["package_type"],
                    "package_count": item["packagetype_quantity"],
                    "medicine_quantity": item["purchase_quantity"]
                })

            purchases_by_store_date.append({
                "purchase_id": purchase_id,
                "store_id": purchase["store_id"],
                "store_name": store_name,
                "purchase_date": purchase_date,
                "distributor_id": purchase["distributor_id"],
                "distributor_name": distributor_name,
                "purchased_amount": total_amount,
                "invoice_number": purchase["invoice_number"],
                "purchase_items": purchase_items
            })
        return purchases_by_store_date
    except Exception as e:
        logger.error(f"Database error in fetching the purchase in date range BL: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in fetching the purchase in date range BL: " + str(e))

async def delete_purchase_collection_bl(purchase_id: str, db=Depends(get_database)):
    
    """
    Deleting the purchase collection from the database.
    """
    try:
        delete_purchase = await delete_purchase_collection_dal(purchase_id=purchase_id, db=db)
        return PurchaseMessage(message="Purchase Deleted Successfully") #delete_purchase
    except Exception as e:
        logger.error(f"Database error in deleting the purchase: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error in deleting the purchase: " + str(e))
    