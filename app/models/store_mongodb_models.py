from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime
from ...app.models.store_mongodb_eunums import OrderStatus, PaymentMethod, MedicineForms, UnitsInPack, Package

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class OrderItem(BaseModel):
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine master table")
    quantity: int = Field(..., description="Quantity of the ordered medicine")
    price: float = Field(..., description="Price of the ordered medicine")
    unit: constr(max_length=255) = Field(..., description="unit of the ordered medicine")
    class Config:
        arbitrary_types_allowed = True

class Order(BaseModel):
    
    """
    Base model for the Order collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    customer_id: str = Field(..., description="Customer ObjectID from the Customer Collection") # from customer id
    order_date: datetime = Field(..., description="Order Date")
    order_status: OrderStatus = Field(..., description="Order Status can be pending, processing, shipped, delivered, cancelled ")  # "pending", "processing", "shipped", "delivered", "cancelled"
    payment_method: PaymentMethod = Field(..., description="Payment Method can be Online, Cash, Cash on delivery")  # "online", "cash", "cod"
    total_amount: float = Field(..., description="Total amount of the ordered items")
    order_items: List[OrderItem] = Field(..., description="Order_items List of items ")
    class Config:
        arbitrary_types_allowed = True

class SaleItem(BaseModel):
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    batch_id: str = Field(..., description="Batch ObjectID from the stock ObjectID") # this id should contain the stock id
    expiry_date: datetime = Field(..., description="Expiry date of a medicine")
    quantity: int = Field(..., description="Quantity of the medicine")
    price: float = Field(..., description="Price of the medicine")
    class Config:
        arbitrary_types_allowed = True

class Sale(BaseModel):
    
    """
    Base model for the Sale collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    sale_date: datetime = Field(..., description="Sale Date")
    customer_id: str = Field(..., description="Customer OBjectId from the customer collection") 
    total_amount: float = Field(..., description="Total amount of the saled medicine")
    invoice_id: int = Field(..., description="invoice ID of the bill")
    sale_items: List[SaleItem] = Field(..., description="List of Saled medicines")
    class Config:
        arbitrary_types_allowed = True

class BatchDetails(BaseModel):
    expiry_date: datetime = Field(..., description="Expity date of the batch medicines")
    units_in_pack: UnitsInPack = Field(..., description="Units In Pack for the batch medicines")
    batch_quantity: int = Field(..., description="Batch quantity of the batch medicines")
    batch_number: constr(max_length=255) = Field(..., description="Batch number for the medicines") # added new field according to the review
    class config:
        arbitrary_types_allowed = True

class Stock(BaseModel):
    
    """
    Base model for the Stock collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    medicine_form: MedicineForms = Field(..., description="Medicine form can liquid, tablet, injuction, capsule, powder")
    available_stock: int = Field(..., description="Available stock of total medicines in batchs")
    batch_details: List[BatchDetails] = Field(..., description="batch details")
    class Config:
        arbitrary_types_allowed = True

class PurchaseItem(BaseModel):
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    batch_id: str = Field(..., description="Batch ObjectID from the Sales collection")  #from batch details
    expiry_date: str = Field(..., description="Expiry date of the purchased medicine")
    quantity: int = Field(..., description="Quantity of the Purchased Medicine")
    price: float = Field(..., description="Price of the Purchased medicine ")
    manufacture_id: int = Field(..., description="Manufacturer ID from the MYSQL manufaccturer table")
    medicine_form: MedicineForms = Field(..., description="Medicine Form can be liquid, tablet, injection, capsule, powder")
    units_in_pack: UnitsInPack = Field(..., description="Units In Pack can be Ml Count MGMS")
    unit_quantity: int = Field(..., description="Unit Quantity") # n
    package: Package = Field(..., description="Package can be strip, bottle, vial, amp, sachet") # strip/bottle/vial/amp/sachet
    package_count: int = Field(..., description="Package count") # p
    medicine_quantity: int = Field(..., description="Medicine can be a multiple of unit_quantity * package_count") #n*p
    class Config:
        arbitrary_types_allowed = True

class Purchase(BaseModel):
    
    """
    Base model for the Purchase collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    purchase_date: datetime = Field(..., description="Purchase Date of the medicines")
    distributor_id: int = Field(..., description="Distributor ID from the MYSQL distributor table")
    total_amount: float = Field(..., description="Total Amount of the purchased medicines")
    invoice_number : int = Field(..., description="Invoice Number of the purchase bill")
    purchase_items: List[PurchaseItem] = Field(..., description="Purchase items list")
    class Config:
        arbitrary_types_allowed = True

class Pricing(BaseModel):
    
    """
    Base model for the pricing collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="medicine ID from the MYSQL medicine_mastrer table")
    price: float = Field(..., description="Price of the Medicine")
    mrp: float = Field(..., description="MRP of the medicine")
    discount: float = Field(..., description="Discount of the Medicine")
    net_rate: float = Field(..., description="NET Rate of the medicine")
    is_active: bool = Field(..., description="Is Active True or False")
    last_updated_by: str = Field(..., description="Last Updated can be a user_name or user_id from the MYSQL user table") # user id or name of the person who last updated
    updated_on: datetime = Field(..., description="updated on")
    class Config:
        arbitrary_types_allowed = True

class Customer(BaseModel):
    
    """
    Base model for the Customer collection.
    """
      
    name: constr(max_length=255) = Field(..., description="Customer Name")
    mobile: constr(max_length=15) = Field(..., description="Customer Mobile")
    email: constr(max_length=255) = Field(..., description="Customer Email")
    password_hash: constr(max_length=255) = Field(..., description="Customer Password Hashed")
    doctor_name: constr(max_length=255) = Field(..., description="Customer Doctor Name")
    class Config:
        arbitrary_types_allowed = True

class MedicineAvailability(BaseModel):
    
    """
    Base model for the Medicine Availability collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    available_quantity: int = Field(..., description="Medicine Availabiliry for the particular medicine")
    last_updated: datetime = Field(..., description="Last Updated")
    updated_by: constr(max_length=255) = Field(..., description="Updated by Either can be a User_id or user_name from the MYSQL user table")
    class Config:
        arbitrary_types_allowed = True
    