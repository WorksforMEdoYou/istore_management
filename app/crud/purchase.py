from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from sqlalchemy.orm import Session
from ..db.mongodb import get_database
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster, Distributor, Manufacturer, StoreDetails
from ..models.store_mongodb_models import Purchase
import logging
from datetime import datetime
from ..utils import get_name_by_id, validate_by_id

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_purchase_collection_db(purchase, db, mysql_db: Session):
    """
    Creating the purchase collection in the database.
    """
    try:
        # Distributor validation
        distributor_validation = validate_by_id(id=purchase["distributor_id"], model=Distributor, field="distributor_id", db=mysql_db)
        if distributor_validation == "unique":
            raise HTTPException(status_code=404, detail="Distributor not Found.")
        
        purchase_items = []
        for item in purchase["purchase_items"]:
            # medicine validation
            medicine_id = item["medicine_id"]
            if validate_by_id(id=medicine_id, model=MedicineMaster, field="medicine_id", db=mysql_db) == "unique":
                raise HTTPException(status_code=404, detail="Medicine not found")
            # manufacturer validation
            manufacturer_id = item["manufacture_id"]
            if validate_by_id(id=manufacturer_id, model=MedicineMaster, field="manufacturer_id", db=mysql_db) == "unique":
                raise HTTPException(status_code=404, detail="Manufacturer not found")
            
            # stock
            stock = {
                "expiry_date": item["expiry_date"],
                "units_in_pack": item["packagetype_quantity"],
                "batch": item["purchase_quantity"],
                "batch_number": item["batch_number"],
                "is_active": 1
            }
            # Update stock in the database
            await db.stocks.update_one(
                {"store_id": purchase["store_id"], "medicine_id": medicine_id},
                {
                    "$push": {"batch_details": stock},
                    "$inc": {"available_stock": item["purchase_quantity"]},
                    "$set": {"updated_at": datetime.now()}
                },
                upsert=True
            )
            logger.info("Updated in stocks")
            
            purchase_items.append({
                "medicine_id": medicine_id,
                "batch_number": item["batch_number"],
                "expiry_date": item["expiry_date"],
                "manufacture_id": item["manufacture_id"],
                "medicine_form": item["medicine_form"],
                "package_type": item["package_type"],
                "units_per_package_type": item["units_per_package_type"],
                "packagetype_quantity": item["packagetype_quantity"],
                "purchase_mrp": item["purchase_mrp"],
                "purchase_discount": item["purchase_discount"],
                "purchase_amount": item["purchase_amount"],
                "purchase_quantity": item["purchase_quantity"]
            })
        
        result = {
            "store_id": purchase["store_id"],
            "purchase_date": purchase["purchase_date"],
            "distributor_id": purchase["distributor_id"],
            "purchased_amount": purchase["purchased_amount"],
            "invoice_number": purchase["invoice_number"],  # Corrected field name
            "discount": purchase["discount"],
            "mrp": purchase["mrp"],
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
            "active_flag": 1,
            "purchase_items": purchase_items
        }
        results = await db.purchases.insert_one(result)
        result["_id"] = str(results.inserted_id)
        logger.info(f"Purchase created with ID: {result['_id']}")
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def get_all_purchases_db(store_id: int, db, mysql_db: Session):
    """
    Get all purchases from the database
    """
    try:
        result = []
        purchases_cursor = db.purchases.find({"store_id": store_id, "active_flag": 1})
        async for purchase in purchases_cursor:
            purchase_id = str(purchase["_id"])
            purchase_date = str(purchase["purchase_date"])

            distributor_name = get_name_by_id(id=purchase["distributor_id"], model=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            if distributor_name == "unique":
                raise HTTPException(status_code=400, detail="Distributor not Found")

            store_name = get_name_by_id(id=purchase["store_id"], model=StoreDetails, field="store_id", name_field="store_name", db=mysql_db)
            if store_name == "unique":
                raise HTTPException(status_code=400, detail="Store not Found")
            total_amount = str(purchase["purchased_amount"])

            purchase_items = []
            for item in purchase["purchase_items"]:
                medicine_name = get_name_by_id(id=item["medicine_id"], model=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
                if medicine_name == "unique":
                    raise HTTPException(status_code=400, detail="Medicine not Found")

                manufacturer_name = get_name_by_id(id=item["manufacture_id"], model=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
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

            result.append({
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
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_purchases_by_id_db(id: str, db, mysql_db: Session):
    """
    Get purchase by ID from the database
    """
    try:
        result = []
        purchase = await db.purchases.find_one({"_id": ObjectId(id)})
        if purchase:
            purchase_id = str(purchase["_id"])
            purchase_date = str(purchase["purchase_date"])

            distributor_name = get_name_by_id(id=purchase["distributor_id"], model=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            if distributor_name == "unique":
                raise HTTPException(status_code=400, detail="Distributor not Found")

            store_name = get_name_by_id(id=purchase["store_id"], model=StoreDetails, field="store_id", name_field="store_name", db=mysql_db)
            if store_name == "unique":
                raise HTTPException(status_code=400, detail="Store not Found")
            
            total_amount = str(purchase["purchased_amount"])

            purchase_items = []
            for item in purchase["purchase_items"]:
                medicine_name = get_name_by_id(id=item["medicine_id"], model=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
                if medicine_name == "unique":
                    raise HTTPException(status_code=400, detail="Medicine not Found")

                manufacturer_name = get_name_by_id(id=item["manufacture_id"], model=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
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

            result.append({
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
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_purchases_by_date_db(store_id: int, db, mysql_db: Session, start_date: str = None, end_date: str = None):
    """
    Get all purchases from the database store start_date and end_date
    """
    try:
        result = []
        if start_date and end_date:
            # Parse the start and end dates
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Fetch purchases from MongoDB within the date range
            purchases_cursor = db.purchases.find({
                "store_id": store_id,
                "active_flag": 1,
                "purchase_date": {"$gte": start_date, "$lte": end_date}
            })
        else:
            # Fetch all purchases from MongoDB
            purchases_cursor = db.purchases.find({"store_id": store_id, "active_flag": 1})

        purchases = await purchases_cursor.to_list(length=None)
        for purchase in purchases:
            purchase_id = str(purchase["_id"])
            purchase_date = str(purchase["purchase_date"])

            distributor_name = get_name_by_id(id=purchase["distributor_id"], model=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            if distributor_name == "unique":
                raise HTTPException(status_code=400, detail="Distributor not Found")

            store_name = get_name_by_id(id=purchase["store_id"], model=StoreDetails, field="store_id", name_field="store_name", db=mysql_db) 
            if store_name == "unique":
                raise HTTPException(status_code=400, detail="Store not Found")
            
            total_amount = str(purchase["purchased_amount"])

            purchase_items = []
            for item in purchase["purchase_items"]:
                medicine_name = get_name_by_id(id=item["medicine_id"], model=MedicineMaster, field="medicine_id", name_field="medicine_name", db=mysql_db)
                if medicine_name == "unique":
                    raise HTTPException(status_code=400, detail="Medicine not Found")

                manufacturer_name = get_name_by_id(id=item["manufacture_id"], model=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
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

            result.append({
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
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_purchase_collection_db(purchase_id: str, db=Depends(get_database)):
    
    """
    Deleting the purchase collection from the database.
    """
    try:
        delete_result = await db.purchases.update_one(
            {"_id": ObjectId(str(purchase_id))}, 
            {"$set": {"active_flag":0}})
        if delete_result.modified_count == 1:
            return {"message": "Purchase deleted successfully", "purchase_id": purchase_id}
        raise HTTPException(status_code=404, detail="Purchase not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))