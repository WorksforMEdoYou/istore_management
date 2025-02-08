from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
import logging
from .db.mysql_session import get_db
from .models.store_mysql_models import StoreDetails as StoreDetailsModel
from .schemas.StoreDetailsSchema import StoreDetailsCreate
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from .models.store_mysql_models import InvoiceLookup

# configuring the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Check whether entity is available
def check_name_available_utils(name:str, table, field:str, db:Session):
    """
    Checking the field available in the table
    """
    try:
        entity = db.query(table).filter(getattr(table, field) == name).first()
        if entity:
            return entity
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

# Check whether the store exists
def check_store_exists_utils(store: StoreDetailsCreate, db: Session):
    """
    Store validation by email or mobile
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            or_(
            StoreDetailsModel.email == store.email,
            StoreDetailsModel.mobile == store.mobile
            )).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
# cheacking wether the store is allready present in the database
def store_validation_mobile_utils(mobile:str, db: Session = get_db):
    """
    Store validation by mobile number
    """
    try:
        store = db.query(StoreDetailsModel).filter(
            StoreDetailsModel.mobile == mobile
            ).first()
        if store:
            return store
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

#check id validation
def validate_by_id_utils(id:int, table, field:str, db:Session):
    """
    validation by the id to compare the mysql with mongodb
    """
    try:
        entity_data = db.query(table).filter(getattr(table, field) == id).first()
        if entity_data:
            return entity_data
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def get_name_by_id_utils(id:int, table, field:str, name_field:str, db:Session):
    """
    Get the name by the id
    """
    try:
        entity_name = db.query(table).filter(getattr(table, field) == id).first()
        if entity_name:
            return getattr(entity_name, name_field)
        else:
            return "unique"
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

def check_id_available_mongodb_utils(id:str, table:str, db):
    """
    checking the recored available in mongodb
    """
    try:
        mongo_entity = db[table].find_one({"_id": ObjectId(str(id))})
        if mongo_entity:
            return mongo_entity
        else:
            return "unique"
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
def discount(mrp, discount):
    """
    Discounted price
    """
    
    price = mrp - (mrp * discount / 100)
    return price

async def create_sale_invoice(store_id: int, mysql_db: Session):
    """
    Create a new sale invoice.
    """
    try:
        # Logic for the invoice => "MED242500001" -> "MED242500002"
        invoice_details = mysql_db.query(InvoiceLookup).filter(InvoiceLookup.store_id == store_id).order_by(InvoiceLookup.invoicelookup_id.desc()).first()
        if not invoice_details:
            raise HTTPException(status_code=404, detail="Previous invoice not found")
        previous_invoice = invoice_details.last_invoice_number
        new_invoice = previous_invoice[:7] + str(int(previous_invoice[7:]) + 1).zfill(len(previous_invoice) - 7)
        invoices = InvoiceLookup(
            store_id=store_id,
            last_invoice_number=new_invoice,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            active_flag=1
        )
        mysql_db.add(invoices)
        mysql_db.commit()
        return new_invoice
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error: " + str(e))