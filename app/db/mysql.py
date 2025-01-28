from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Rajesh_2002@localhost/istore')

# Create engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("MYSQL Database connection established successfully.")
except SQLAlchemyError as e:
    logger.error(f"Error connecting to the MYSQL database: {str(e)}")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()  # Directly use the defined SessionLocal
    try:
        yield db
    finally:
        db.close()