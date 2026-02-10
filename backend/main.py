from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import asyncio
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Legacy Modernization API",
    version="3.0",
    description="Complete VB to Modern Stack Modernization Platform"
)

# CORS setup
origins = ["http://localhost:4200", "http://localhost:5500", "http://127.0.0.1:4200", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory
OUTPUT_DIR = "/mnt/user-data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import the complete orchestrator
try:
    from graph.enhanced_orchestrator_final import build_enhanced_graph, modernize_stream
    graph = build_enhanced_graph()
    logger.info("✅ Loaded complete enhanced orchestrator (v3.0)")
except Exception as e:
    logger.error(f"❌ Could not load orchestrator: {e}")
    graph = None

# Health check
@app.get("/")
def root():
    return {
        "status": "Backend running",
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Real-time streaming",
            "Business logic analysis",
            "Use case generation",
            "Domain model extraction",
            "Domain model comparison",
            "Backend design (Spring Boot)",
            "Frontend design (Angular)",
            "Cloud architecture (AWS)",
            "Deployable frontend code (ZIP)",
            "Deployable backend code (ZIP)"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "orchestrator": "loaded" if graph else "error"
    }

# Main streaming endpoint with ALL features
@app.post("/chat/stream")
async def chat_stream_complete(req: Request):
    """
    Complete modernization endpoint with:
    - Real-time streaming (no buffering)
    - Use case generation
    - Domain model comparison (optional)
    - Deployable code generation (frontend + backend ZIPs)
    """
    logger.info("=" * 80)
    logger.info("🚀 Starting complete modernization workflow v3.0")
    logger.info("=" * 80)
    
    body = await req.json()
    vb_code = body.get("message", "")
    target_domain = body.get("targetDomainModel", "")
    
    logger.info(f"📄 VB Code: {len(vb_code)} characters")
    if target_domain:
        logger.info(f"🎯 Target Domain Model: {len(target_domain)} characters")
    
    async def event_generator():
        # Initialize state with all fields
        state = {
            "vb_files": [{"filename": "uploaded.vb", "content": vb_code}],
            "target_domain_model": target_domain,
            "history": [],
            "use_case_document": "",
            "business_logic": "",
            "domain_model": "",
            "domain_mapping": "",
            "backend_design": "",
            "frontend_design": "",
            "cloud_design": "",
            "frontend_zip_path": "",
            "backend_zip_path": ""
        }

        try:
            step_count = 0
            current_step = ""
            
            logger.info("🔄 Starting enhanced streaming workflow...")
            
            # Stream each chunk immediately
            async for chunk in modernize_stream(state):
                step_count += 1
                
                # Log step transitions
                for key in chunk.keys():
                    if key != current_step and key in [
                        "business_logic", "use_cases", "domain_model", 
                        "domain_mapping", "backend_design", "frontend_design", 
                        "cloud_design", "frontend_code_status", "backend_code_status"
                    ]:
                        current_step = key
                        step_names = {
                            "business_logic": "🔍 Business Logic Analysis",
                            "use_cases": "📋 Use Case Generation",
                            "domain_model": "🏗️  Domain Model Extraction",
                            "domain_mapping": "🔄 Domain Model Comparison",
                            "backend_design": "⚙️  Backend Design",
                            "frontend_design": "🎨 Frontend Design",
                            "cloud_design": "☁️  Cloud Architecture",
                            "frontend_code_status": "💻 Frontend Code Generation",
                            "backend_code_status": "💻 Backend Code Generation"
                        }
                        logger.info(f"{step_names.get(key, key)}: Processing...")
                
                # Convert file paths to download URLs if present
                if "frontend_zip_path" in chunk and chunk["frontend_zip_path"]:
                    filename = os.path.basename(chunk["frontend_zip_path"])
                    chunk["frontend_zip_url"] = f"http://127.0.0.1:8000/download/{filename}"
                    logger.info(f"✅ Frontend ZIP ready: {filename}")
                
                if "backend_zip_path" in chunk and chunk["backend_zip_path"]:
                    filename = os.path.basename(chunk["backend_zip_path"])
                    chunk["backend_zip_url"] = f"http://127.0.0.1:8000/download/{filename}"
                    logger.info(f"✅ Backend ZIP ready: {filename}")
                
                # Send chunk immediately
                yield f"data: {json.dumps(chunk)}\n\n"
                
                # CRITICAL: Force immediate delivery (prevent buffering)
                await asyncio.sleep(0)
            
            logger.info("✅ Workflow completed successfully!")
            logger.info(f"📊 Total chunks processed: {step_count}")
            
        except Exception as e:
            logger.error(f"❌ Error during workflow: {str(e)}", exc_info=True)
            error_data = {"error": str(e), "step": "error"}
            yield f"data: {json.dumps(error_data)}\n\n"

    # Return with anti-buffering headers
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

# File download endpoint
@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated ZIP files."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(file_path):
        logger.info(f"📥 Downloading: {filename}")
        return FileResponse(
            file_path,
            filename=filename,
            media_type="application/zip"
        )
    
    logger.error(f"❌ File not found: {filename}")
    return {"error": "File not found", "filename": filename}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Legacy Modernization API v3.0")
    logger.info("Features: Streaming, Use Cases, Domain Mapping, Code Generation")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
