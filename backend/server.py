from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import uuid
import zipfile
import shutil
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'app_generator_db')

# Initialize MongoDB client with retry logic
try:
    client = AsyncIOMotorClient(mongo_url)
    # Force a connection to verify it works
    logging.info("Testing MongoDB connection...")
    db = client[db_name]
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")
    # Continue without MongoDB for now
    client = None
    db = None

# OpenAI API key - this will be provided by the user
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Directory for storing generated code and zip files
GENERATED_CODE_DIR = ROOT_DIR / 'generated_code'
GENERATED_CODE_DIR.mkdir(exist_ok=True)

# Define Models
class AppGenerationRequest(BaseModel):
    appDescription: str
    model: str = "gpt-4"  # Default to GPT-4

class AppGenerationResponse(BaseModel):
    generationId: str

class GenerationStatus(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str  # "pending", "in_progress", "completed", "failed"
    logs: List[str] = []
    zipUrl: Optional[str] = None
    error: Optional[str] = None
    appDescription: str
    model: str
    timestamp: float = Field(default_factory=lambda: __import__('time').time())

# Function to call OpenAI API
async def call_openai_api(prompt, model="gpt-4"):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not provided")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert full-stack web developer. Your task is to generate complete, working code for web applications based on the user's description. Generate all necessary files for a complete, standalone web application."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {str(e)}")
        raise

# Function to call Anthropic API
async def call_anthropic_api(prompt, model="claude-3-opus"):
    if not ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key not provided")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert full-stack web developer. Your task is to generate complete, working code for web applications based on the user's description. Generate all necessary files for a complete, standalone web application."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except Exception as e:
        logging.error(f"Error calling Anthropic API: {str(e)}")
        raise

# Function to parse code blocks from LLM response
def parse_code_files(response_text):
    files = []
    lines = response_text.split('\n')
    current_file = None
    current_content = []
    
    for line in lines:
        if line.startswith('```') and len(line) > 3:
            # Start of a new code block with filename
            if current_file:
                # Save previous file
                files.append({
                    'filename': current_file,
                    'content': '\n'.join(current_content)
                })
            
            # Extract filename from markdown code block
            file_info = line[3:].strip()
            if ':' in file_info:
                current_file = file_info.split(':', 1)[1].strip()
            else:
                current_file = file_info.strip()
            
            current_content = []
        elif line.strip() == '```' and current_file:
            # End of a code block
            files.append({
                'filename': current_file,
                'content': '\n'.join(current_content)
            })
            current_file = None
            current_content = []
        elif current_file is not None:
            # Inside a code block
            current_content.append(line)
    
    return files

# Background task for generating app code
async def generate_app_code(generation_id: str, app_description: str, model: str):
    # Create a directory for this generation
    generation_dir = GENERATED_CODE_DIR / generation_id
    generation_dir.mkdir(exist_ok=True)
    
    # Helper function to update generation status
    async def update_status(update_dict, push_dict=None):
        # Update in-memory storage
        app.state.generation_statuses = getattr(app.state, 'generation_statuses', {})
        if generation_id in app.state.generation_statuses:
            status_dict = app.state.generation_statuses[generation_id]
            status_dict.update(update_dict)
            
            # Handle logs appending
            if push_dict and 'logs' in push_dict:
                if 'logs' not in status_dict:
                    status_dict['logs'] = []
                status_dict['logs'].extend(push_dict['logs'])
        
        # Update in MongoDB if available
        if db is not None:
            try:
                # Prepare update operation
                update_ops = {"$set": update_dict}
                if push_dict:
                    update_ops["$push"] = push_dict
                
                await db.generation_status.update_one(
                    {"id": generation_id},
                    update_ops
                )
            except Exception as e:
                logging.error(f"Failed to update generation status in MongoDB: {str(e)}")
    
    try:
        # Update status to in_progress
        await update_status({"status": "in_progress"})
        
        # Add log entry
        await update_status({}, {"logs": ["Starting code generation..."]})
        
        # Prepare prompt for the AI
        prompt = f"""
        Generate a complete, working web application based on the following description:
        
        "{app_description}"
        
        Return the code as a set of files in markdown format. For each file, use the format:
        
        ```filename: path/to/file.ext
        // File content here
        ```
        
        Include ALL necessary files to make the application work, including:
        - HTML/CSS/JavaScript files
        - Backend code if required
        - Package.json or other dependency files
        - README.md with setup instructions
        
        Make sure the application is complete, functional, and follows best practices.
        """
        
        # Add log entry
        await update_status({}, {"logs": [f"Sending request to AI model: {model}..."]})
        
        # Call appropriate AI API based on model selection
        if model.startswith("gpt"):
            response_text = await call_openai_api(prompt, model)
        elif model.startswith("claude"):
            response_text = await call_anthropic_api(prompt, model)
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        # Add log entry
        await update_status({}, {"logs": ["AI response received. Parsing generated code..."]})
        
        # Parse the response to extract code files
        files = parse_code_files(response_text)
        
        if not files:
            raise Exception("No valid code files found in the AI response")
        
        # Add log entry
        await update_status({}, {"logs": [f"Found {len(files)} files in AI response. Creating file structure..."]})
        
        # Write files to disk
        for file_info in files:
            filename = file_info['filename']
            content = file_info['content']
            
            # Create subdirectories if needed
            file_path = generation_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Add log entry
            await update_status({}, {"logs": [f"Created file: {filename}"]})
        
        # Create a zip file of the generated code
        zip_path = str(GENERATED_CODE_DIR / f"{generation_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(str(generation_dir)):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, str(generation_dir))
                    zipf.write(file_path, arcname)
        
        # Add log entry
        await update_status({}, {"logs": ["Created ZIP archive of generated code."]})
        
        # Update status to completed
        zip_url = f"/api/download/{generation_id}"
        await update_status({
            "status": "completed",
            "zipUrl": zip_url
        })
        
    except Exception as e:
        logging.error(f"Error in generate_app_code: {str(e)}")
        # Update status to failed
        await update_status({
            "status": "failed",
            "error": str(e)
        }, {"logs": [f"Error: {str(e)}"]})
        
        # Clean up
        if generation_dir.exists():
            shutil.rmtree(str(generation_dir))

# API Endpoints
@api_router.post("/generate-app", response_model=AppGenerationResponse)
async def generate_app(request: AppGenerationRequest, background_tasks: BackgroundTasks):
    # Check if API keys are available based on the selected model
    if request.model.startswith("gpt") and not OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    elif request.model.startswith("claude") and not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=400, detail="Anthropic API key not configured")
    
    if not request.appDescription.strip():
        raise HTTPException(status_code=400, detail="App description cannot be empty")
    
    # Generate a unique ID for this generation
    generation_id = str(uuid.uuid4())
    
    # Create a status document in the database
    status = GenerationStatus(
        id=generation_id,
        status="pending",
        appDescription=request.appDescription,
        model=request.model
    )
    
    # Store status in memory if MongoDB is not available
    app.state.generation_statuses = getattr(app.state, 'generation_statuses', {})
    app.state.generation_statuses[generation_id] = status.dict()
    
    # Try to store in MongoDB if available
    if db is not None:
        try:
            await db.generation_status.insert_one(status.dict())
        except Exception as e:
            logging.error(f"Failed to store generation status in MongoDB: {str(e)}")
    
    # Start the generation in the background
    background_tasks.add_task(
        generate_app_code,
        generation_id,
        request.appDescription,
        request.model
    )
    
    return AppGenerationResponse(generationId=generation_id)

@api_router.get("/generation-status/{generation_id}")
async def get_generation_status(generation_id: str):
    status = None
    
    # Try to get from MongoDB first if available
    if db is not None:
        try:
            status = await db.generation_status.find_one({"id": generation_id})
        except Exception as e:
            logging.error(f"Failed to retrieve generation status from MongoDB: {str(e)}")
    
    # Fall back to in-memory storage
    if status is None:
        app.state.generation_statuses = getattr(app.state, 'generation_statuses', {})
        status = app.state.generation_statuses.get(generation_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    return status

@api_router.get("/download/{generation_id}")
async def download_zip(generation_id: str):
    status = None
    
    # Try to get from MongoDB first if available
    if db is not None:
        try:
            status = await db.generation_status.find_one({"id": generation_id})
        except Exception as e:
            logging.error(f"Failed to retrieve generation status from MongoDB: {str(e)}")
    
    # Fall back to in-memory storage
    if status is None:
        app.state.generation_statuses = getattr(app.state, 'generation_statuses', {})
        status = app.state.generation_statuses.get(generation_id)
    
    if not status or status.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Generated ZIP not found")
    
    zip_path = GENERATED_CODE_DIR / f"{generation_id}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    return FileResponse(
        path=str(zip_path),
        filename=f"generated_app_{generation_id}.zip",
        media_type="application/zip"
    )

@api_router.get("/")
async def root():
    return {"message": "Hello World", "status": "API is operational"}

@api_router.post("/setup-api-keys")
async def setup_api_keys(api_keys: Dict[str, str]):
    global OPENAI_API_KEY, ANTHROPIC_API_KEY
    
    if "openai" in api_keys:
        OPENAI_API_KEY = api_keys["openai"]
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
    if "anthropic" in api_keys:
        ANTHROPIC_API_KEY = api_keys["anthropic"]
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    
    return {"message": "API keys updated successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
