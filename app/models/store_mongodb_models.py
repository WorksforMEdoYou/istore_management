from bson import ObjectId
from pydantic import BaseModel, Field, constr
from typing import List, Text
from datetime import datetime
from ..models.store_mongodb_eunums import OrderStatus, PaymentMethod, MedicineForms, UnitsInPack, PackageType

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
    batch_id: str = Field(..., description="Batch id from stock") 
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
    #invoice_id: str = Field(..., description="invoice ID of the bill")
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
    batch_number: str = Field(..., description="Batch if from the purchased person")  
    expiry_date: datetime = Field(..., description="Expiry date of the purchased medicine")
    #quantity: int = Field(..., description="Quantity of the Purchased Medicine")
    manufacture_id: int = Field(..., description="Manufacturer ID from the MYSQL manufaccturer table")
    medicine_form: MedicineForms = Field(..., description="Medicine Form can be liquid, tablet, injection, capsule, powder")
    
    #units_in_pack: UnitsInPack = Field(..., description="Units In Pack can be Ml Count MGMS")
    #unit_quantity: int = Field(..., description="Unit Quantity") # n
    package_type: PackageType = Field(..., description="Package type can be strip, bottle, vial, amp, sachet") # strip/bottle/vial/amp/sachet
    units_per_package_type:int = Field(..., description="packackage type no of medicines")
    packagetype_quantity: int = Field(..., description="packackage medicnes available in the unit per package type")
    purchase_quantity: int = Field(..., description="total quantity in medicine")
    #package_count: int = Field(..., description="Package count") # p
    #medicine_quantity: int = Field(..., description="Medicine can be a multiple of unit_quantity * package_count") #n*p
    
    purchase_mrp: float = Field(..., description="mrp of the purchased medicine")
    purchase_discount: float = Field(..., description="discount per medicine")
    purchase_amount: float = Field(..., description="purchased amount")
    class Config:
        arbitrary_types_allowed = True

class Purchase(BaseModel):
    
    """
    Base model for the Purchase collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    purchase_date: datetime = Field(..., description="Purchase Date of the medicines")
    distributor_id: int = Field(..., description="Distributor ID from the MYSQL distributor table")
    purchased_amount: float = Field(..., description="Total Amount of the purchased medicines")
    invoice_number : str = Field(..., description="Invoice Number of the purchase bill")
    discount:float = Field(..., description="discount of the purchasesd medicine")
    mrp: float = Field(..., description="mrp of the purchaed mediciene")
    purchase_items: List[PurchaseItem] = Field(..., description="Purchase items list")
    class Config:
        arbitrary_types_allowed = True

class Pricing(BaseModel):
    
    """
    Base model for the pricing collection.
    """
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="medicine ID from the MYSQL medicine_mastrer table")
    #price: float = Field(..., description="Price of the Medicine") #the pricice can be differ by mrp and discount
    mrp: float = Field(..., description="MRP of the medicine")
    discount: float = Field(..., description="Discount of the Medicine")
    net_rate: float = Field(..., description="NET Rate of the medicine")
    is_active: bool = Field(..., description="Is Active True or False")
    last_updated_by: str = Field(..., description="Last Updated can be a user_name or user_id from the MYSQL user table") # user id or name of the person who last updated
    
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

""" class MedicineAvailability(BaseModel):
    
    
    Base model for the Medicine Availability collection.
    
    
    store_id: int = Field(..., description="Store ID from the MYSQL store_details table")
    medicine_id: int = Field(..., description="Medicine ID from the MYSQL medicine_master table")
    available_quantity: int = Field(..., description="Medicine Availabiliry for the particular medicine")
    last_updated: datetime = Field(..., description="Last Updated")
    updated_by: constr(max_length=255) = Field(..., description="Updated by Either can be a User_id or user_name from the MYSQL user table")
    class Config:
        arbitrary_types_allowed = True """
    