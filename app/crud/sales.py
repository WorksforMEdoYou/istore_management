from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_sale_collection_db(sale: Sale, db):
    """
    Creating the sale collection in the database.
    """
    try:
        sale_dict = sale.dict(by_alias=True)
        for sales in sale_dict["sale_items"]:
            store_id = sale_dict["store_id"]
            medicine_id = sales["medicine_id"]
            quantity = sales["quantity"]

            # Get the active stocks
            stocks = await db["stocks"].find_one({"store_id": store_id, "medicine_id": medicine_id, "active_flag": 1})
            if not stocks:
                raise HTTPException(status_code=404, detail="Stock not found")

            # Sort the batches by expiry date
            batches = sorted(stocks["batch_details"], key=lambda x: x["expiry_date"])

            for batch in batches:
                if batch["expiry_date"] < datetime.now() or (batch["expiry_date"] - datetime.now()).days <= 30:
                    # Update the batch if the medicine is expired or going to expire in 30 days
                    await db["stocks"].update_one(
                        {"store_id": store_id, "medicine_id": medicine_id, "batch_details.batch_number": batch["batch_number"]},
                        {"$set": {"batch_details.$.is_active": 0}}
                    )
                else:
                    if batch["is_active"] == 1:
                        if quantity > batch["units_in_pack"]:
                            quantity -= batch["units_in_pack"]
                            # Update the stock
                            await db["stocks"].update_one(
                                {"store_id": store_id, "medicine_id": medicine_id, "batch_details.batch_number": batch["batch_number"]},
                                {"$set": {"batch_details.$.units_in_pack": 0, "updated_at": datetime.now()}}
                            )
                        else:
                            # Update the stock
                            await db["stocks"].update_one(
                                {"store_id": store_id, "medicine_id": medicine_id, "batch_details.batch_number": batch["batch_number"]},
                                {"$set": {"batch_details.$.units_in_pack": batch["units_in_pack"] - quantity, "updated_at": datetime.now()}}
                            )
                            quantity = 0
                            break

        result = {
            "store_id": sale_dict["store_id"],
            "sale_date": str(sale_dict["sale_date"]),
            "customer_id": str(sale_dict["customer_id"]),
            "total_amount": sale_dict["total_amount"],
            "invoice_id": sale_dict["invoice_id"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active_flag": 1,
            "sale_items": sale_dict["sale_items"]
        }
        await db["sales"].insert_one(result)
        return result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
async def read_sales_db(store_id: int, db):
    try:
        sales = []
        async for sale in db.sales.find({"store_id": store_id, "active_flag":1}):
            sale["_id"] = str(sale["_id"])
            sales.append(sale)
        
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sale_particular_db(sale_id: str, db):
    """
    Get sale particular
    """
    try:
        result = await db["sales"].find_one({"_id": ObjectId(sale_id)})
        if result:
            result["_id"] = str(result["_id"])
            return result
        raise HTTPException(status_code=404, detail="Sale not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_sale_collection_db(sale_id: str, db):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_result = await db.sales.update_one({"_id": ObjectId(sale_id)}, {"$set": {"active_flag": 0}})
        if delete_result.modified_count == 1:
            return {
                "sale_id": sale_id,
                "message": "Sale order deleted successfully"
            }
        raise HTTPException(status_code=404, detail="Sale order not found")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))