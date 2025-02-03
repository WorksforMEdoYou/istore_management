from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import category, store, distributor, manufacturer, medicinemaster, purchase, pricing, orders, stocks, sales
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import logging

app = FastAPI()

# Custom JSON encoder for ObjectId
def json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Override default JSONEncoder with custom JSONEncoder
app.json_encoder = json_encoder

#mySQl

app.include_router(category.router, prefix="/storeapi", tags=["Category"])
app.include_router(store.router, prefix="/storeapi", tags=["Store"])
app.include_router(distributor.router, prefix="/storeapi", tags=["Distributor"])
app.include_router(manufacturer.router, prefix="/storeapi", tags=["Manufacturer"])
app.include_router(medicinemaster.router, prefix="/storeapi", tags=["Medicine Master"])

#mongoDB
app.include_router(purchase.router, prefix="/storeapi", tags=["Purchase"])
app.include_router(pricing.router, prefix="/storeapi", tags=["Pricing"])
app.include_router(orders.router, prefix="/storeapi", tags=["Orders"])
app.include_router(stocks.router, prefix="/storeapi", tags=["Stocks"])
app.include_router(sales.router, prefix="/storeapi", tags=["Sales"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

# Startup Event
@app.on_event("startup")
async def on_startup():
    logger.info("App is starting...")
# Initialize database connection
@app.get("/")
def read_root():
    return {"message": "Welcome to the Istore"}

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
