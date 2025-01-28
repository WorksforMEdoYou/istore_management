from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv

#load enviroment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Access the environment variables
MONGO_DETAILS = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
collection_name = os.getenv("COLLECTION_NAME", "istores")

try:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    database = client[collection_name]
    logger.info("Successfully connected to the MongoDB.")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    database = None

def get_database():
    if database is None:
        logger.error("Database connection is not established.")
        raise RuntimeError("Database connection is not established.")
    return database
