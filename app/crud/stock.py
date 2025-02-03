from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Stock
import logging
from sqlalchemy.orm import Session
from ..db.mysql_session import get_db
from ..models.store_mysql_models import MedicineMaster, Manufacturer, Category, Distributor, StoreDetails
from bson import ObjectId
from datetime import datetime
from ..utils import get_name_by_id

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_stock_collection_db(stocks, db=Depends(get_database)):
    """
    Creating the stock collection in the database.
    """
    try:
        result = await db.stocks.insert_one(stocks)
        stocks["_id"] = str(result.inserted_id)
        logger.info(f"stock created with ID: {stocks['_id']}")
        return stocks
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_all_stocks_by_store_db(store_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    """
    Get all stocks by store id.
    """
    try:
        result = []
        cursor = db.stocks.find({"store_id": store_id})
        stocks = await cursor.to_list(length=None)
        if stocks:
            for stock in stocks:
                is_stock = "In Stock" if stock["available_stock"] > 0 else "Not In Stock"
                store_name = get_name_by_id(id=store_id, model=StoreDetails, field="store_id", name_field="store_name", db=mysql_db)
                medicine_id = stock["medicine_id"]
                medicines = mysql_db.query(MedicineMaster).filter(MedicineMaster.medicine_id == medicine_id).first()
                if not medicines:
                    raise HTTPException(status_code=404, detail="Medicine not found")
                medicine_name = medicines.medicine_name
                medicine_composition = medicines.composition
                manufacturer_id = medicines.manufacturer_id
                manufacturer_name = get_name_by_id(id=manufacturer_id, model=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
                category_id = medicines.category_id
                category_name = get_name_by_id(id=category_id, model=Category, field="category_id", name_field="category_name", db=mysql_db)
                pricings = await db.pricing.find_one({"store_id": store_id, "medicine_id": medicine_id})
                if pricings:
                    price = pricings["price"]
                    discount = pricings["discount"]
                    net_rate = pricings["net_rate"]
                else:
                    price = discount = net_rate = None
                packages_cursor = db.purchases.find({"store_id": store_id, "purchase_items.medicine_id": medicine_id})
                async for package in packages_cursor:
                    for item in package["purchase_items"]:
                        if item["medicine_id"] == medicine_id:
                            packets = item["units_per_package_type"]
                            units = item["packagetype_quantity"]
                            result.append({
                                "store_id": store_id,
                                "store_name": store_name,
                                "medicine_id": medicine_id,
                                "medicine_name": medicine_name,
                                "manufacturer_name": manufacturer_name,
                                "Is_stock": is_stock,
                                "packets": packets,
                                "units": units,
                                "available_stock": stock["available_stock"],
                                "mrp": price,
                                "discount": discount,
                                "net_rate": net_rate,
                                "composition": medicine_composition,
                                "category": category_name
                            })
            return result
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_stock_collection_by_id_db(store_id: int, medicine_id: int, db=Depends(get_database), mysql_db: Session = Depends(get_db)):
    """
    Getting the stock collection by id from the database.
    """
    try:
        batches = []
        stocks = db.stocks.find({"store_id": store_id, "medicine_id": medicine_id})
        async for stock in stocks:
            for item in stock["batch_details"]:
                if item["is_active"] == 1:
                    is_stock_batches = "In stock" if item["batch"] > 0 else "Not In Stock"
                    batch_number = item['batch_number']
                    batch_expiry_date = str(item["expiry_date"])
                    available_quantity = item["batch"]
                    
                    pricing_cursor = db.pricing.find({"store_id": store_id, "medicine_id": medicine_id})
                    async for price in pricing_cursor:
                        price_value = price["price"]
                        discount = price["discount"]
                        net_rate = price["net_rate"]
                        mrp = price["mrp"]
                        batches.append({
                            "is_stock": is_stock_batches,
                            "batch_number": batch_number,
                            "batch_expiry_date": batch_expiry_date,
                            "available_quantity": available_quantity,
                            "price": price_value,
                            "discount": discount,
                            "net_rate": net_rate,
                            "mrp": mrp
                        })
        
        # Sort batches by expiry_date
        batches = sorted(batches, key=lambda x: x["batch_expiry_date"])
        
        purchases_list = []
        purchases = db.purchases.find({"store_id": store_id, "purchase_items.medicine_id": medicine_id}).skip(0).limit(10)
        async for purchase in purchases:
            purchase_date = str(purchase["purchase_date"])
            purchase_distributor_id = purchase["distributor_id"]
            purchase_distributor_name = get_name_by_id(id=purchase_distributor_id, model=Distributor, field="distributor_id", name_field="distributor_name", db=mysql_db)
            for item in purchase["purchase_items"]:
                if item["medicine_id"] == medicine_id:
                    purchase_expiry = item["expiry_date"]
                    purchase_batch_number = item["batch_number"]
                    purchase_quantity = item["purchase_quantity"]
                    purchase_amount = item["purchase_amount"]
                    
                    purchases_list.append({
                        "purchase_date": purchase_date,
                        "purchase_distributor_name": purchase_distributor_name,
                        "purchase_medicine_expiry_date": purchase_expiry,
                        "purchase_medicine_batch_number": purchase_batch_number,
                        "purchase_medicine_quantity": purchase_quantity,
                        "purchase_medicine_amount": purchase_amount
                    })
        sales_list = []
        sales = db.sales.find({"store_id": store_id, "sale_items.medicine_id": medicine_id}).skip(0).limit(10)
        async for sale in sales:
            sale_date = str(sale["sale_date"])
            sale_invoice_number = sale["invoice_id"]
            customer_details = sale["customer_id"]
            customer = await db.customers.find_one({"_id": ObjectId(customer_details)})
            if customer:
                customer_name = customer["name"]
                doctor_name = customer.get("doctor_name", None)
                
                for item in sale["sale_items"]:
                    if item["medicine_id"] == medicine_id:
                        sale_quantity = item["quantity"]
                        sale_price = item["price"]
                        sale_batch = item["batch_id"]
                        sale_expiry_date = item["expiry_date"]
                        
                        sales_list.append({
                            "sale_date": sale_date,
                            "invoice_number": sale_invoice_number,
                            "customer_name": customer_name,
                            "doctor_name": doctor_name,
                            "sale_medicine_quantity": sale_quantity,
                            "sale_medicine_price": sale_price,
                            "sale_medicine_batch": sale_batch,
                            "sale_expiry_date": sale_expiry_date
                        })
                        
        substitute_list = []
        medicine_composition = mysql_db.query(MedicineMaster).filter(MedicineMaster.medicine_id == medicine_id).first()
        if medicine_composition:
            medicine_composition_name = medicine_composition.composition
            substitute_medicines = mysql_db.query(MedicineMaster).filter(MedicineMaster.composition == medicine_composition_name).all()
            for substitute in substitute_medicines:
                substitute_medicine_name = substitute.medicine_name
                substitute_medicine_id = substitute.medicine_id
                substitute_manufacturer = get_name_by_id(id=substitute.manufacturer_id, model=Manufacturer, field="manufacturer_id", name_field="manufacturer_name", db=mysql_db)
                
                substitute_stock = await db.stocks.find_one({"store_id": store_id, "medicine_id": substitute_medicine_id})
                if substitute_stock:
                    is_substitute_stock = "In Stock" if substitute_stock["available_stock"] > 0 else "Not In Stock"
                    substitute_stock_quantity = substitute_stock["available_stock"]
                else:
                    is_substitute_stock = "Not In Stock"
                    substitute_stock_quantity = 0
                
                substitute_pricing = await db.pricing.find_one({"store_id": store_id, "medicine_id": substitute_medicine_id})
                if substitute_pricing:
                    substitute_price = substitute_pricing["price"]
                    substitute_net_rate = substitute_pricing["net_rate"]
                else:
                    substitute_price = substitute_net_rate = None
                
                substitute_list.append({
                    "store_id": store_id,
                    "substitute_medicine_id": substitute_medicine_id,
                    "is_stock": is_substitute_stock,
                    "substitute_medicine_name": substitute_medicine_name,
                    "substitute_manufacturer": substitute_manufacturer,
                    "substitute_stock_quantity": substitute_stock_quantity,
                    "substitute_price": substitute_price,
                    "net_rate": substitute_net_rate
                })
        
        result = {
            "store_id": store_id,
            "medicine_id": medicine_id,
            "batches": batches,
            "purchases": purchases_list,
            "sales": sales_list,
            "substitutes": substitute_list
        }
        
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))    
 
async def delete_stock_collection_db(store_id:int, medicine_id:int, db):
    """
    Deleting the stock collection from the database.
    """
    try:
        delete_result = await db.stocks.update_one({"store_id":store_id, "medicine_id":medicine_id}, {"$set": {"active_flag":0}})
        if delete_result.modified_count == 1:
            return {"store_id": store_id, "medicine_id": medicine_id}
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))