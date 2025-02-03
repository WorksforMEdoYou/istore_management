from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .Base import Base
from .store_mysql_eunums import StoreStatus, UserRole, StoreVerification

class StoreDetails(Base):
    __tablename__ = 'store_details'
    
    """
    SQLAlchemy model for the StoreDetails table.
    """

    store_id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(255), doc="store name for the store")
    license_number = Column(String(50), doc="license number for the store")
    gst_state_code = Column(String(10), doc="GST State Code for the store")
    gst_number = Column(String(50), doc="GST Number for the store")
    pan = Column(String(10), doc="PAN Number for the store")
    address = Column(Text, doc="Address of the store")
    email = Column(String(100), doc="Email Address for the store")
    mobile = Column(String(15), doc="Modile number for the store")
    owner_name = Column(String(255), doc="Owner name of the store")
    is_main_store = Column(Boolean, doc="Is Main of the stores")
    latitude = Column(DECIMAL(10, 6), doc="Latitude of the store")
    longitude = Column(DECIMAL(10, 6), doc="Longitude of the store")
    status = Column(Enum(StoreStatus), doc="Status of the store Active, InActive, Closed")
    # new fileds added
    remarks = Column(Text, doc="Remarks for the store")
    verification_status = Column(Enum(StoreVerification), doc="Store verification can be pending, verified")
    active_flag = Column(Integer, doc="0 at creation or 1 active or 2 suspended")
    created_at = Column(DateTime, doc="Date and time when the store was created")
    updated_at = Column(DateTime, doc="Date and time when the store was updated")
    users = relationship('User', back_populates='store')
  
class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    
    """
    SQLAlchemy model for the manufacturer table.
    """

    manufacturer_id = Column(Integer, primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255), doc="manufacturer_name for the medicine_master")
    created_at = Column(DateTime, doc="manufacturer created at")
    updated_at = Column(DateTime, doc="manufacturer updated at")
    active_flag = Column(Integer, doc="0 or 1")
    medicines = relationship("MedicineMaster", back_populates="manufacturer")

class Category(Base):
    __tablename__ = 'category'
    
    """
    SQLAlchemy model for the category table.
    """
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), doc="category name of the medicine")
    created_at = Column(DateTime, doc="category created at")
    updated_at = Column(DateTime, doc="category updated at")
    active_flag = Column(Integer, doc="0 or 1")
    medicines = relationship("MedicineMaster", back_populates="category")

class MedicineMaster(Base):
    __tablename__ = 'medicine_master'
    
    """
    SQLAlchemy model for the medicine_master table.
    """
    
    medicine_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(255), doc="Name of the medicine")
    generic_name = Column(String(255), doc="Generic name of the medicine")
    hsn_code = Column(String(10), doc="HSN code of the medicine")
    formulation = Column(String(50), doc="Formula of the medicine")
    strength = Column(String(50), doc="Stength of the medicine")
    unit_of_measure = Column(String(10), doc="Unit of Measure of the medicine")
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.manufacturer_id'), doc="ID of the Manufacturer")
    category_id = Column(Integer, ForeignKey('category.category_id'), doc="ID of the Category")
    created_at = Column(DateTime, doc="medicine created at")
    updated_at = Column(DateTime, doc="medicine updated at")
    active_flag = Column(Integer, doc="0 or 1")
    composition = Column(String(255), doc="Composition of the medicine")
    manufacturer = relationship("Manufacturer", back_populates="medicines")
    category = relationship("Category", back_populates="medicines")
    
class Distributor(Base):
    __tablename__ = 'distributor'
    
    """
    SQLAlchemy model for the distributor table.
    """
    
    distributor_id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_name = Column(String(255), doc="distributor name for medicine_master")
    created_at = Column(DateTime, doc="distributor created at")
    updated_at = Column(DateTime, doc="distributor updated at")
    active_flag = Column(Integer, doc="0 or 1")

class User(Base): # for store users
    __tablename__ = 'users'
    
    """
    SQLAlchemy model for the user table.
    """
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), doc="Name of the User")
    password_hash = Column(String(255), doc="User password hashed")
    role = Column(Enum(UserRole), doc="role of the User Shop Keeper, Admin, Consumer")
    store_id = Column(Integer, ForeignKey('store_details.store_id'), doc="Store ID from the store_details table")
    store = relationship('StoreDetails', back_populates='users')
    
class InvoiceLookup(Base):
    __tablename__ = 'invoice_lookup'
     
    """
    SQLAlchemy model for the invoice to imporove sales
    """
    
    invoicelookup_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, doc="store_id")
    last_invoice_number = Column(String(255), doc="last invloice number")
    created_at = Column(DateTime, doc="created time")
    updated_at = Column(DateTime, doc="updated time")
    active_flag = Column(Integer, doc="active or inactive")