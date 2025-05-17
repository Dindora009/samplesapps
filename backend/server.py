from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import base64
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import requests
from openai import OpenAI

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Get OpenAI API key from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
def get_openai_client():
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found in environment variables")
        raise HTTPException(status_code=500, detail="API configuration error")
    return OpenAI(api_key=OPENAI_API_KEY)

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class TryOnRequest(BaseModel):
    person_image: str  # Base64 encoded image
    clothing_image: str  # Base64 encoded image

class TryOnResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    result_image: str  # Base64 encoded image
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TryOnHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    person_image: str  # Base64 encoded image
    clothing_image: str  # Base64 encoded image
    result_image: str  # Base64 encoded image
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper function to decode base64 to bytes
def decode_base64_to_bytes(base64_string):
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        logger.error(f"Error decoding base64: {e}")
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/try-on", response_model=TryOnResult)
async def create_try_on(request: TryOnRequest, openai_client: OpenAI = Depends(get_openai_client)):
    try:
        logger.info("Processing try-on request")
        
        # Convert person and clothing images from base64 to binary
        person_image_bytes = decode_base64_to_bytes(request.person_image)
        clothing_image_bytes = decode_base64_to_bytes(request.clothing_image)
        
        # Save images temporarily
        person_image_path = os.path.join(ROOT_DIR, "temp_person.png")
        clothing_image_path = os.path.join(ROOT_DIR, "temp_clothing.png")
        
        with open(person_image_path, "wb") as f:
            f.write(person_image_bytes)
        
        with open(clothing_image_path, "wb") as f:
            f.write(clothing_image_bytes)
        
        # Use OpenAI to generate try-on image
        logger.info("Calling OpenAI API for image generation")
        try:
            result = openai_client.images.edit(
                model="gpt-image-1",
                image=[
                    open(person_image_path, "rb"),
                    open(clothing_image_path, "rb"),
                ],
                prompt="Generate a realistic image of the person wearing the clothing item. The clothing should be properly fitted to the person's body, with realistic lighting, shadows, and fabric draping. Make it look like a natural photograph of the person wearing the item."
            )
            
            # Get base64 encoded result
            result_image_base64 = result.data[0].b64_json
            
            # Save try-on history to database
            try_on_history = TryOnHistory(
                person_image=request.person_image,
                clothing_image=request.clothing_image,
                result_image=result_image_base64
            )
            
            await db.try_on_history.insert_one(try_on_history.model_dump())
            
            # Create and return result
            try_on_result = TryOnResult(
                result_image=result_image_base64
            )
            
            return try_on_result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Try-on processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary files
        for temp_file in [person_image_path, clothing_image_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")

@api_router.get("/try-on/history", response_model=List[TryOnHistory])
async def get_try_on_history():
    try:
        history = await db.try_on_history.find().sort("created_at", -1).to_list(100)
        return [TryOnHistory(**item) for item in history]
    except Exception as e:
        logger.error(f"Error retrieving try-on history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
