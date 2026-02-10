from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import shutil
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import subprocess
import tempfile
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Legacy Modernization API", version="2.0")

# CORS setup
origins = ["http://localhost:4200", "http://localhost:5500", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    files: Optional[List[dict]] = None
    targetDomainModel: Optional[str] = None
    step: Optional[str] = None

# Upload directory
UPLOAD_DIR = "/tmp/vb_uploads"
OUTPUT_DIR = "/tmp/modernization_output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import graph - try enhanced first, fallback to standard
graph = None
use_enhanced = False

try:
    from graph.enhanced_orchestrator import build_enhanced_graph, modernize_stream
    graph = build_enhanced_graph()
    use_enhanced = True
    logger.info("✅ Loaded enhanced orchestrator (V2)")
except Exception as e:
    logger.warning(f"⚠️ Could not load enhanced orchestrator: {e}")
    logger.info("📦 Falling back to standard orchestrator (V1)")
    try:
        from graph.orchestrator import build_graph, analyze_stream
        graph = build_graph()
        use_enhanced = False
    except Exception as e2:
        logger.error(f"❌ Could not load any orchestrator: {e2}")
        # We'll handle this in the endpoints

# Health check
@app.get("/")
def root():
    return {
        "status": "Backend running",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "orchestrator": "enhanced" if use_enhanced else "standard",
        "features": [
            "Multi-file VB project upload",
            "Requirements document generation",
            "Domain mapping",
            "Deployable code generation"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "graph_type": "enhanced" if use_enhanced else "standard"
    }

# Legacy endpoint for V1 Angular app compatibility
@app.post("/chat/stream")
async def chat_stream_legacy(req: Request):
    """
    Legacy endpoint for backward compatibility with V1 Angular app
    Converts single-file format to multi-file format
    """
    logger.info("=" * 80)
    logger.info("🚀 Starting modernization workflow (legacy endpoint)")
    logger.info("=" * 80)
    
    body = await req.json()
    vb_code = body.get("message", "")
    
    logger.info(f"📄 Received VB code: {len(vb_code)} characters")
    
    # Convert single file to multi-file format
    vb_files = [{"filename": "uploaded.vb", "content": vb_code}]
    
    async def event_generator():
        state = {
            "vb_files": vb_files,
            "target_domain_model": "",
            "history": [],
            "requirements_doc": "",
            "business_logic": "",
            "domain_model": "",
            "domain_mapping": "",
            "backend_design": "",
            "frontend_design": "",
            "cloud_design": "",
            "generated_code": ""
        }

        try:
            step_number = 0
            current_step = ""
            
            logger.info("🔄 Starting streaming workflow...")
            
            # Use the correct way to invoke the graph
            if use_enhanced:
                # For enhanced orchestrator - call the function directly
                from graph.enhanced_orchestrator import modernize_stream
                
                async for chunk in modernize_stream(state):
                    step_number += 1
                    
                    # Detect which step we're in
                    if "requirements_doc" in chunk:
                        if current_step != "requirements":
                            current_step = "requirements"
                            logger.info("📋 Step 1: Generating Requirements Document...")
                        logger.debug(f"  Requirements chunk #{step_number}")
                        
                    elif "business_logic" in chunk:
                        if current_step != "business_logic":
                            current_step = "business_logic"
                            logger.info("🔍 Step 2: Analyzing Business Logic...")
                        logger.debug(f"  Business logic chunk #{step_number}")
                        
                    elif "domain_model" in chunk:
                        if current_step != "domain_model":
                            current_step = "domain_model"
                            logger.info("🏗️  Step 3: Extracting Domain Model...")
                        logger.debug(f"  Domain model chunk #{step_number}")
                        
                    elif "domain_mapping" in chunk:
                        if current_step != "domain_mapping":
                            current_step = "domain_mapping"
                            logger.info("🔄 Step 4: Mapping Domains...")
                        logger.debug(f"  Domain mapping chunk #{step_number}")
                        
                    elif "backend_design" in chunk:
                        if current_step != "backend_design":
                            current_step = "backend_design"
                            logger.info("⚙️  Step 5: Designing Backend Architecture...")
                        logger.debug(f"  Backend design chunk #{step_number}")
                        
                    elif "frontend_design" in chunk:
                        if current_step != "frontend_design":
                            current_step = "frontend_design"
                            logger.info("🎨 Step 6: Designing Frontend Components...")
                        logger.debug(f"  Frontend design chunk #{step_number}")
                        
                    elif "cloud_design" in chunk:
                        if current_step != "cloud_design":
                            current_step = "cloud_design"
                            logger.info("☁️  Step 7: Planning Cloud Deployment...")
                        logger.debug(f"  Cloud design chunk #{step_number}")
                        
                    elif "generated_code" in chunk:
                        if current_step != "generated_code":
                            current_step = "generated_code"
                            logger.info("💻 Step 8: Generating Code...")
                        logger.debug(f"  Code generation chunk #{step_number}")
                    
                    # Send to client
                    yield f"data: {json.dumps(chunk)}\n\n"
                    await asyncio.sleep(0.01)
            else:
                # For standard orchestrator (V1)
                from graph.orchestrator import analyze_stream
                
                # Convert state to V1 format
                v1_state = {
                    "vb_code": vb_code,
                    "history": [],
                    "business_logic": "",
                    "domain_model": "",
                    "backend_design": "",
                    "frontend_design": "",
                    "cloud_design": ""
                }
                
                async for chunk in analyze_stream(v1_state):
                    step_number += 1
                    
                    # Detect step
                    for key in ["business_logic", "domain_model", "backend_design", "frontend_design", "cloud_design"]:
                        if key in chunk:
                            if current_step != key:
                                current_step = key
                                step_names = {
                                    "business_logic": "🔍 Business Logic Analysis",
                                    "domain_model": "🏗️  Domain Model",
                                    "backend_design": "⚙️  Backend Design",
                                    "frontend_design": "🎨 Frontend Design",
                                    "cloud_design": "☁️  Cloud Architecture"
                                }
                                logger.info(f"{step_names.get(key, key)}...")
                    
                    yield f"data: {json.dumps(chunk)}\n\n"
                    await asyncio.sleep(0.01)
            
            logger.info("✅ Workflow completed successfully!")
            logger.info(f"📊 Total chunks processed: {step_number}")
            
        except Exception as e:
            logger.error(f"❌ Error during workflow: {str(e)}", exc_info=True)
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Enhanced modernization endpoint
@app.post("/modernize/stream")
async def modernize_stream_endpoint(req: Request):
    """
    Enhanced streaming endpoint with multi-file support
    """
    logger.info("=" * 80)
    logger.info("🚀 Starting enhanced modernization workflow")
    logger.info("=" * 80)
    
    body = await req.json()
    vb_files = body.get("files", [])
    target_domain = body.get("targetDomainModel", "")
    
    logger.info(f"📁 Processing {len(vb_files)} VB files")
    if target_domain:
        logger.info(f"🎯 Target domain model provided: {len(target_domain)} chars")
    
    async def event_generator():
        state = {
            "vb_files": vb_files,
            "target_domain_model": target_domain,
            "history": [],
            "requirements_doc": "",
            "business_logic": "",
            "domain_model": "",
            "domain_mapping": "",
            "backend_design": "",
            "frontend_design": "",
            "cloud_design": "",
            "generated_code": ""
        }

        try:
            step_number = 0
            current_step = ""
            
            logger.info("🔄 Starting enhanced streaming workflow...")
            
            # Import and call the streaming function directly
            from graph.enhanced_orchestrator import modernize_stream
            
            async for chunk in modernize_stream(state):
                step_number += 1
                
                # Log step transitions
                for key in chunk.keys():
                    if key != current_step:
                        current_step = key
                        step_names = {
                            "requirements_doc": "📋 Requirements Document",
                            "business_logic": "🔍 Business Logic Analysis",
                            "domain_model": "🏗️  Domain Model Extraction",
                            "domain_mapping": "🔄 Domain Mapping",
                            "backend_design": "⚙️  Backend Design",
                            "frontend_design": "🎨 Frontend Design",
                            "cloud_design": "☁️  Cloud Architecture",
                            "generated_code": "💻 Code Generation"
                        }
                        logger.info(f"{step_names.get(key, key)}: Processing...")
                
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)
            
            logger.info("✅ Enhanced workflow completed!")
            logger.info(f"📊 Total chunks: {step_number}")
            
        except Exception as e:
            logger.error(f"❌ Workflow error: {str(e)}", exc_info=True)
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# File upload endpoint
@app.post("/upload/vb-project")
async def upload_vb_project(files: List[UploadFile] = File(...)):
    """
    Upload multiple VB files (entire project)
    """
    logger.info(f"📤 Uploading {len(files)} files")
    uploaded_files = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        logger.info(f"  ⬆️  {file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read content for analysis
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        uploaded_files.append({
            "filename": file.filename,
            "path": file_path,
            "size": os.path.getsize(file_path),
            "type": file.filename.split(".")[-1].lower(),
            "content": content[:1000]  # Preview only
        })
    
    logger.info(f"✅ Upload complete: {len(uploaded_files)} files")
    return {
        "message": f"Uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Legacy Modernization API v2.0")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
