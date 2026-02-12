from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from pathlib import Path
from graph.enhanced_orchestrator_final import modernize_stream_with_approval
from utils.domain_mapping_excel import export_domain_mapping_to_excel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "VB Modernization Backend Running", "version": "3.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "features": ["streaming", "stage_approval", "domain_comparison", "excel_export"]}

# Main streaming endpoint with stage approval
@app.post("/chat/stream")
async def chat_stream_with_approval(req: Request):
    """
    Complete modernization endpoint with:
    - Stage-by-stage processing
    - User approval workflow
    - Domain model comparison (optional)
    - Deployable code generation
    """
    logger.info("=" * 80)
    logger.info("🚀 Starting modernization workflow v3.0 (Stage Approval)")
    logger.info("=" * 80)
    
    body = await req.json()
    vb_code = body.get("message", "")
    target_domain = body.get("targetDomainModel", "")
    
    logger.info(f"📄 VB Code: {len(vb_code)} characters")
    if target_domain:
        logger.info(f"🎯 Target Domain Model: {len(target_domain)} characters")
    
    async def event_generator():
        # Initialize state
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
            "backend_zip_path": "",
            "current_stage": "",
            "stage_approved": False
        }

        try:
            current_stage = ""
            
            logger.info("🔄 Starting stage-based workflow...")
            
            # Stream each chunk
            async for chunk in modernize_stream_with_approval(state):
                # Log stage transitions
                if "stage" in chunk and chunk["stage"] != current_stage:
                    current_stage = chunk["stage"]
                    stage_names = {
                        "business_logic": "🔍 Business Logic Analysis",
                        "use_cases": "📋 Use Case Generation",
                        "domain_model": "🏗️ Domain Model Extraction",
                        "domain_mapping": "🔄 Domain Model Comparison",
                        "backend_design": "⚙️ Backend Design",
                        "frontend_design": "🎨 Frontend Design",
                        "cloud_design": "☁️ Cloud Architecture",
                        "frontend_code": "💻 Frontend Code Generation",
                        "backend_code": "💻 Backend Code Generation",
                        "complete": "✅ Complete"
                    }
                    logger.info(f"{stage_names.get(current_stage, current_stage)}: Started")
                
                # Check if stage is complete - PAUSE FOR APPROVAL
                if chunk.get("stage_complete", False):
                    logger.info(f"⏸️ Stage complete: {current_stage} - Waiting for user approval")
                
                # Convert file paths to download URLs
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
                await asyncio.sleep(0)
            
            logger.info("✅ Workflow completed!")
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            error_data = {"error": str(e), "stage": "error"}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# Excel export endpoint for domain mapping
@app.post("/export/domain-mapping/excel")
async def export_domain_mapping(req: Request):
    """
    Export domain mapping comparison to Excel file.
    
    Request body:
    {
        "domain_mapping": "JSON string from domain_mapping_agent"
    }
    """
    try:
        body = await req.json()
        domain_mapping_json = body.get("domain_mapping", "")
        
        if not domain_mapping_json:
            return {"error": "No domain mapping provided"}
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_filename = f"domain_mapping_{timestamp}.xlsx"
        output_path = f"/mnt/user-data/outputs/{output_filename}"
        
        # Create Excel file
        excel_path = export_domain_mapping_to_excel(domain_mapping_json, output_path)
        
        logger.info(f"✅ Excel file created: {excel_path}")
        
        # Return file for download
        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating Excel: {str(e)}", exc_info=True)
        return {"error": str(e)}

# File download endpoint
@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated ZIP files or other outputs."""
    file_path = f"/mnt/user-data/outputs/{filename}"
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(file_path, filename=filename)

# Endpoint to get list of available outputs
@app.get("/outputs")
async def list_outputs():
    """List all available output files."""
    output_dir = Path("/mnt/user-data/outputs")
    
    if not output_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "download_url": f"http://127.0.0.1:8000/download/{file_path.name}"
            })
    
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)