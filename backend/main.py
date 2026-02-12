from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Legacy Modernization API", version="3.0")

# CORS setup
origins = ["http://localhost:4200", "http://localhost:5500", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import orchestrator
try:
    from graph.enhanced_orchestrator_final import modernize_stream as modernize_stream_function
    orchestrator_loaded = True
    logger.info("✅ Enhanced orchestrator loaded successfully")
except Exception as e:
    orchestrator_loaded = False
    logger.error(f"❌ Could not load orchestrator: {e}")
    modernize_stream_function = None

@app.get("/")
def root():
    return {
        "status": "Backend running",
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "orchestrator_loaded": orchestrator_loaded
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "orchestrator": "loaded" if orchestrator_loaded else "not loaded"
    }

@app.post("/chat/stream")
async def chat_stream_legacy(req: Request):
    """
    Legacy endpoint for backward compatibility
    """
    logger.info("=" * 80)
    logger.info("🚀 Starting modernization workflow")
    logger.info("=" * 80)
    
    if not orchestrator_loaded:
        async def error_gen():
            yield f"data: {json.dumps({'error': 'Orchestrator not loaded'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")
    
    body = await req.json()
    vb_code = body.get("message", "")
    target_domain = body.get("targetDomainModel", "")
    
    logger.info(f"📄 VB code: {len(vb_code)} chars")
    if target_domain:
        logger.info(f"🎯 Target domain: {len(target_domain)} chars")
    
    async def event_generator():
        # FIXED: Include ALL required state keys
        state = {
            "vb_files": [{"filename": "uploaded.vb", "content": vb_code}],
            "target_domain_model": target_domain,
            "history": [],
            "requirements_doc": "",
            "business_logic": "",
            "use_cases": "",              # ✅ Frontend expects this
            "use_case_document": "",      # ✅ Orchestrator might use this
            "domain_model": "",
            "domain_mapping": "",
            "backend_design": "",
            "frontend_design": "",
            "cloud_design": "",
            "generated_code": "",
            "frontend_code_status": "",
            "backend_code_status": "",
            "frontend_zip_url": "",
            "backend_zip_url": ""
        }

        try:
            step_number = 0
            current_step = ""
            
            logger.info("🔄 Starting enhanced streaming workflow...")
            
            async for chunk in modernize_stream_function(state):
                step_number += 1
                
                # Detect which step
                for key in chunk.keys():
                    if key != current_step:
                        current_step = key
                        step_names = {
                            "requirements_doc": "📋 Requirements Document",
                            "business_logic": "🔍 Business Logic",
                            "use_cases": "📝 Use Cases",
                            "use_case_document": "📝 Use Case Document",
                            "domain_model": "🏗️ Domain Model",
                            "domain_mapping": "🔄 Domain Mapping",
                            "backend_design": "⚙️ Backend Design",
                            "frontend_design": "🎨 Frontend Design",
                            "cloud_design": "☁️ Cloud Architecture",
                            "generated_code": "💻 Code Generation",
                            "frontend_zip_url": "📦 Frontend ZIP",
                            "backend_zip_url": "📦 Backend ZIP"
                        }
                        logger.info(f"{step_names.get(key, key)}: Processing...")
                
                # Map use_case_document to use_cases for frontend compatibility
                if "use_case_document" in chunk and "use_cases" not in chunk:
                    chunk["use_cases"] = chunk["use_case_document"]
                
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)
            
            logger.info("✅ Workflow completed!")
            logger.info(f"📊 Total chunks: {step_number}")
            
        except Exception as e:
            logger.error(f"❌ Error during workflow: {str(e)}", exc_info=True)
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Legacy Modernization API v3.0")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
