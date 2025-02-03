from fastapi import Depends, HTTPException
from bson import ObjectId
from typing import List
from ..db.mongodb import get_database
from ..models.store_mongodb_models import Sale
import logging
from ..crud.sales import create_sale_collection_db, get_sale_particular_db, read_sales_db, delete_sale_collection_db
from datetime import datetime
from sqlalchemy.orm import Session
from ..utils import create_sale_invoice

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_sale_collection(sale: Sale, db, mysql_db: Session):
    """
    Creating the sale collection in the database.
    """
    try:
        sale_dict = sale.dict(by_alias=True)
        
        store_id = sale_dict["store_id"]
        # Generate the invoice number
        invoice_number = await create_sale_invoice(store_id=store_id, mysql_db=mysql_db)
        sale_dict["invoice_number"] = invoice_number
        
        for sales in sale_dict["sale_items"]:
            medicine_id = sales["medicine_id"]
            quantity = sales["quantity"]

            # Get the active stocks
            stocks = await db["stocks"].find_one({"store_id": store_id, "medicine_id": medicine_id, "active_flag": 1})
            if not stocks:
                raise HTTPException(status_code=404, detail="Stock not found")

            # Sort the batches by expiry date
            batches = sorted(stocks["batch_details"], key=lambda x: x["expiry_date"])
            
            # Get the batch by batch
            for batch in batches:
                
                # checking the batch is expired or the medicine will expired in one month (30 days)
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
            "invoice_id": invoice_number,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active_flag": 1,
            "sale_items": sale_dict["sale_items"]
        }
        sales_result = await create_sale_collection_db(sale=result, db=db)
        return sales_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sales(store_id:int, db):
    """
    Get the sale by store
    """
    try:
        sales = await read_sales_db(store_id=store_id, db=db)
        return sales
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def get_sale_particular(sale_id: str, db):
    """
    Get the sale particular
    """
    try:
        sale = await get_sale_particular_db(sale_id=sale_id, db=db)
        return sale
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

async def delete_sale_collection(sale_id: str, db):
    """
    Deleting the sale collection from the database.
    """
    try:
        delete_result = await delete_sale_collection_db(sale_id=sale_id, db=db)
        return delete_result
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
