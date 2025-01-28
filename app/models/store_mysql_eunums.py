from enum import Enum

class StoreStatus(str, Enum):
    
    """
    Enum for Store Status
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

class UserRole(str, Enum):
    
    """
    Enum for User Role
    """
    SHOP_KEEPER = "store_keeper" 
    ADMIN = "admin" 
    CONSUMER = "consumer"

class StoreVerification(str, Enum):
    
    """
    Enum for Store Verification
    """
    VERIFIED = "verified"
    PENDING = "pending"