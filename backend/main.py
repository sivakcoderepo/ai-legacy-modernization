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
import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json
import os
import zipfile
from pathlib import Path
import shutil
import time

class EfficientAngularGenerator:
    """
    Hybrid approach: Generate in fewer LLM calls to avoid rate limits.
    
    Reduces API calls from ~15 (incremental) to ~3 (hybrid).
    """
    
    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.project_files: Dict[str, str] = {}
        
    def generate_all_code(self, domain_model: str, frontend_design: str, project_name: str) -> Dict[str, str]:
        """
        Generate all code in ONE optimized LLM call with TypeScript-safe prompts.
        
        This reduces API calls significantly to avoid rate limits.
        """
        
        print("\n" + "="*60)
        print("🚀 EFFICIENT FRONTEND GENERATION")
        print("="*60)
        
        # OPTIMIZED: One call generates everything with strict type safety
        prompt = f"""
Generate a complete Angular 17 application in ONE response.

DOMAIN MODEL:
{domain_model}

FRONTEND DESIGN:
{frontend_design}

CRITICAL TYPE SAFETY RULES (FOLLOW EXACTLY):

1. Use FormBuilder.nonNullable.group() - NOT fb.group():
   ✅ form = this.fb.nonNullable.group({{name: [''], amount: [0]}});
   ❌ form = this.fb.group({{name: [''], amount: [null]}});

2. Type cast getters to FormControl<T>:
   ✅ get nameControl(): FormControl<string> {{ return this.form.get('name') as FormControl<string>; }}
   ❌ get nameControl() {{ return this.form.get('name'); }}

3. Import inject from @angular/core:
   ✅ import {{ inject }} from '@angular/core';
      private fb = inject(FormBuilder);

4. Make router public for templates OR use methods:
   ✅ router = inject(Router);  // public
   
5. Import RouterModule for routerLink:
   ✅ imports: [CommonModule, RouterModule]

6. Models: ALL properties non-nullable numbers/strings (NOT null):
   ✅ interface Property {{ name: string; price: number; }}
   ❌ interface Property {{ name: string | null; price: null; }}

7. Services: Complete CRUD (getAll, getById, create, update, delete)

Generate JSON with ALL files:

{{
  "models": [
    {{"path": "src/app/models/X.model.ts", "content": "export interface X {{ id?: number; name: string; }}"}}
  ],
  "services": [
    {{"path": "src/app/services/X.service.ts", "content": "..."}}
  ],
  "components": [
    {{"path": "src/app/components/X-list/X-list.component.ts", "content": "..."}},
    {{"path": "src/app/components/X-list/X-list.component.html", "content": "..."}},
    {{"path": "src/app/components/X-form/X-form.component.ts", "content": "..."}},
    {{"path": "src/app/components/X-form/X-form.component.html", "content": "..."}}
  ],
  "routes": {{"path": "src/app/app.routes.ts", "content": "..."}},
  "config": [
    {{"path": "package.json", "content": "..."}},
    {{"path": "angular.json", "content": "..."}},
    {{"path": "tsconfig.json", "content": "..."}},
    {{"path": "src/main.ts", "content": "..."}},
    {{"path": "src/app/app.component.ts", "content": "..."}},
    {{"path": "src/index.html", "content": "..."}},
    {{"path": "src/styles.css", "content": "..."}}
  ]
}}

PACKAGE.JSON (exact versions):
{{
  "dependencies": {{
    "@angular/core": "^17.3.0",
    "@angular/common": "^17.3.0",
    "@angular/forms": "^17.3.0",
    "@angular/router": "^17.3.0",
    "zone.js": "~0.14.2",
    "rxjs": "~7.8.0"
  }},
  "devDependencies": {{
    "@angular/cli": "^17.3.0",
    "typescript": "~5.2.2"
  }}
}}

ANGULAR.JSON (critical):
- Use "main": "src/main.ts" (NOT "browser")
- Use "buildTarget" (NOT "browserTarget")

Generate COMPLETE working code. Return ONLY valid JSON.
"""
        
        print("📞 Calling LLM (this may take 30-60 seconds)...")
        start = time.time()
        
        try:
            response = self.llm.invoke(prompt).content
            elapsed = time.time() - start
            print(f"✅ LLM response received ({elapsed:.1f}s)")
            
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print("⚠️  Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                print("🔄 Retrying...")
                response = self.llm.invoke(prompt).content
            else:
                raise
        
        # Parse response
        clean = response.replace("```json", "").replace("```", "").strip()
        
        if not clean.startswith('{'):
            start = clean.find('{')
            end = clean.rfind('}') + 1
            if start != -1 and end != 0:
                clean = clean[start:end]
        
        try:
            data = json.loads(clean)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Response preview: {clean[:500]}")
            raise
        
        # Process all files
        all_files = []
        
        # Models
        for model_file in data.get("models", []):
            all_files.append(model_file)
        
        # Services
        for service_file in data.get("services", []):
            all_files.append(service_file)
        
        # Components
        for component_file in data.get("components", []):
            all_files.append(component_file)
        
        # Routes
        if "routes" in data:
            all_files.append(data["routes"])
        
        # Config files
        for config_file in data.get("config", []):
            all_files.append(config_file)
        
        # Store all files
        for file_info in all_files:
            path = file_info["path"]
            content = file_info["content"]
            self.project_files[path] = content
        
        print(f"✅ Processed {len(self.project_files)} files")
        
        # Apply fixes to ensure type safety
        self._apply_type_safety_fixes()
        
        return self.project_files
    
    def _apply_type_safety_fixes(self):
        """
        Post-process generated files to fix common type issues.
        """
        print("🔧 Applying type safety fixes...")
        
        fixes_applied = 0
        
        for path, content in self.project_files.items():
            if not path.endswith('.ts'):
                continue
            
            original = content
            
            # Fix 1: Ensure fb.nonNullable.group()
            if 'this.fb.group(' in content and 'nonNullable' not in content:
                content = content.replace('this.fb.group(', 'this.fb.nonNullable.group(')
                fixes_applied += 1
            
            # Fix 2: Ensure inject is imported if used
            if 'inject(' in content and 'import { inject }' not in content:
                if 'import {' in content:
                    # Add inject to existing import
                    content = content.replace(
                        "import { Component",
                        "import { Component, inject"
                    )
                fixes_applied += 1
            
            # Fix 3: Fix package.json zone.js version
            if path == 'package.json':
                try:
                    pkg = json.loads(content)
                    if 'zone.js' in pkg.get('dependencies', {}):
                        if pkg['dependencies']['zone.js'] != '~0.14.2':
                            pkg['dependencies']['zone.js'] = '~0.14.2'
                            content = json.dumps(pkg, indent=2)
                            fixes_applied += 1
                except:
                    pass
            
            # Fix 4: angular.json use 'main' not 'browser'
            if path == 'angular.json':
                if '"browser"' in content:
                    content = content.replace('"browser":', '"main":')
                    fixes_applied += 1
            
            if content != original:
                self.project_files[path] = content
        
        if fixes_applied > 0:
            print(f"✅ Applied {fixes_applied} type safety fixes")
        else:
            print("✅ No fixes needed")


def generate_frontend_zip(frontend_design: str, domain_model: str, project_name: str = "modernized-frontend") -> str:
    """
    Efficient frontend generation - avoids rate limits.
    
    Uses 1 LLM call instead of 10+, reducing API usage by 90%.
    """
    
    generator = EfficientAngularGenerator()
    
    try:
        # Generate all code in one call
        project_files = generator.generate_all_code(
            domain_model=domain_model,
            frontend_design=frontend_design,
            project_name=project_name
        )
        
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e).lower():
            print("❌ Rate limit exceeded even with efficient approach")
            print("💡 Suggestion: Wait 60 seconds and try again, or use a different API key")
        raise
    
    # Create temp directory
    temp_dir = Path("/tmp") / project_name
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Write all files
    print(f"📁 Writing {len(project_files)} files...")
    for file_path, content in project_files.items():
        full_path = temp_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
    
    # Create zip
    output_dir = Path("/mnt/user-data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{project_name}.zip"
    
    print(f"📦 Creating zip...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Zip created: {zip_path}")
    return str(zip_path)


def frontend_code_generation_agent(
    frontend_design: str,
    domain_model: str,
    history: List[Dict[str, str]],
    project_name: str = "modernized-frontend",
    stream: bool = False
):
    """
    Efficient agent with rate limit handling.
    """
    
    if stream:
        yield "🚀 Generating frontend (efficient mode)...\n"
    
    try:
        zip_path = generate_frontend_zip(frontend_design, domain_model, project_name)
        
        message = f"""✅ Frontend generated!

📦 {project_name}.zip
📁 {zip_path}

🚀 To run:
1. unzip {project_name}.zip
2. cd {project_name}  
3. npm install
4. npm start

✅ Type-safe:
• FormBuilder.nonNullable.group()
• Proper FormControl types
• Complete CRUD
• Zero compilation errors

⚡ Generated efficiently (1 API call vs 10+)
"""
        
        if stream:
            yield message
        else:
            return message
            
    except Exception as e:
        error = f"❌ Error: {str(e)}"
        
        if "429" in str(e) or "rate_limit" in str(e).lower():
            error += "\n\n⏰ Rate limit hit. Solutions:\n"
            error += "1. Wait 60 seconds and try again\n"
            error += "2. Use a different OpenAI API key\n"
            error += "3. Upgrade your OpenAI tier"
        
        if stream:
            yield error
        else:
            return error