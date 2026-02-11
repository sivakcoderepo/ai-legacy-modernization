import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json
import os
import zipfile
from pathlib import Path

def generate_frontend_zip(frontend_design: str, domain_model: str, project_name: str = "modernized-frontend") -> str:
    """
    Generates a complete, deployable Angular application as a zip file.
    
    Args:
        frontend_design: Frontend design specification
        domain_model: Domain model to generate TypeScript interfaces
        project_name: Name of the Angular project
    
    Returns:
        Path to the generated zip file
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    prompt = f"""
You are a senior Angular developer. Generate a COMPLETE, PRODUCTION-READY Angular 17+ standalone application.

FRONTEND DESIGN:
{frontend_design}

DOMAIN MODEL:
{domain_model}

Generate a JSON structure with ALL files needed for a working Angular app that can be deployed immediately:

{{
  "projectName": "{project_name}",
  "files": [
    {{
      "path": "package.json",
      "content": "Complete package.json with all dependencies for Angular 17+"
    }},
    {{
      "path": "angular.json",
      "content": "Complete angular.json configuration"
    }},
    {{
      "path": "tsconfig.json",
      "content": "TypeScript configuration"
    }},
    {{
      "path": "tsconfig.app.json",
      "content": "App-specific TypeScript config"
    }},
    {{
      "path": "src/index.html",
      "content": "Main HTML file"
    }},
    {{
      "path": "src/main.ts",
      "content": "Bootstrap file"
    }},
    {{
      "path": "src/styles.css",
      "content": "Global styles with modern, professional design"
    }},
    {{
      "path": "src/app/app.component.ts",
      "content": "Root component with routing"
    }},
    {{
      "path": "src/app/app.component.html",
      "content": "Root component template"
    }},
    {{
      "path": "src/app/app.component.css",
      "content": "Root component styles"
    }},
    {{
      "path": "src/app/app.routes.ts",
      "content": "Application routing configuration"
    }},
    {{
      "path": "src/app/models/domain.model.ts",
      "content": "TypeScript interfaces for all domain entities"
    }},
    {{
      "path": "src/app/services/api.service.ts",
      "content": "Main API service for backend communication"
    }},
    {{
      "path": "src/app/services/auth.service.ts",
      "content": "Authentication service"
    }},
    {{
      "path": "src/app/components/dashboard/dashboard.component.ts",
      "content": "Dashboard component TypeScript"
    }},
    {{
      "path": "src/app/components/dashboard/dashboard.component.html",
      "content": "Dashboard component HTML with modern UI"
    }},
    {{
      "path": "src/app/components/dashboard/dashboard.component.css",
      "content": "Dashboard component styles"
    }},
    {{
      "path": "src/app/components/entity-list/entity-list.component.ts",
      "content": "List component for main entities"
    }},
    {{
      "path": "src/app/components/entity-list/entity-list.component.html",
      "content": "List component HTML with table/cards"
    }},
    {{
      "path": "src/app/components/entity-list/entity-list.component.css",
      "content": "List component styles"
    }},
    {{
      "path": "src/app/components/entity-form/entity-form.component.ts",
      "content": "Form component for create/edit"
    }},
    {{
      "path": "src/app/components/entity-form/entity-form.component.html",
      "content": "Form component HTML with validation"
    }},
    {{
      "path": "src/app/components/entity-form/entity-form.component.css",
      "content": "Form component styles"
    }},
    {{
      "path": "src/app/components/navbar/navbar.component.ts",
      "content": "Navigation bar component"
    }},
    {{
      "path": "src/app/components/navbar/navbar.component.html",
      "content": "Navigation bar HTML"
    }},
    {{
      "path": "src/app/components/navbar/navbar.component.css",
      "content": "Navigation bar styles"
    }},
    {{
      "path": "src/environments/environment.ts",
      "content": "Development environment config"
    }},
    {{
      "path": "src/environments/environment.prod.ts",
      "content": "Production environment config"
    }},
    {{
      "path": ".gitignore",
      "content": "Git ignore file for Angular"
    }},
    {{
      "path": "README.md",
      "content": "Complete README with setup and deployment instructions"
    }}
  ]
}}

REQUIREMENTS:
1. Use Angular 17+ with standalone components (NO NgModule)
2. Use reactive forms for all forms
3. Include proper error handling and loading states
4. Add responsive design (mobile-first)
5. Include environment configuration for API URLs
6. Add interceptors for HTTP requests
7. Use modern UI/UX patterns (cards, gradients, shadows)
8. Include proper TypeScript types for everything
9. Add validation messages and user feedback
10. Make it production-ready with proper structure

API Endpoint assumed: http://localhost:8080/api

Return ONLY the JSON structure with complete file contents.
"""
    
    response = llm.invoke(prompt).content
    
    # Clean up markdown code blocks if present
    response = response.replace("```json", "").replace("```", "").strip()
    
    try:
        project_data = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Response: {response[:500]}")
        raise
    
    # Create temporary directory structure
    temp_dir = Path("/tmp") / project_name
    temp_dir.mkdir(exist_ok=True)
    
    # Create all files
    for file_info in project_data["files"]:
        file_path = temp_dir / file_info["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_info["content"])
    
    # Create zip file
    zip_path = f"/mnt/user-data/outputs/{project_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    return zip_path


def frontend_code_generation_agent(
    frontend_design: str,
    domain_model: str,
    history: List[Dict[str, str]],
    project_name: str = "modernized-frontend",
    stream: bool = False
):
    """
    Agent that generates deployable frontend code.
    
    Args:
        frontend_design: Frontend design specification
        domain_model: Domain model
        history: Conversation history
        project_name: Name of the project
        stream: Whether to stream the response
    
    Yields:
        Status updates and final zip file path
    """
    if stream:
        yield "🎨 Generating complete Angular application...\n"
        yield "📦 Creating project structure...\n"
    
    try:
        zip_path = generate_frontend_zip(frontend_design, domain_model, project_name)
        
        message = f"""
✅ Frontend code generated successfully!

📦 ZIP File: {zip_path}
📁 Project Name: {project_name}

🚀 To run the application:
1. Unzip the file: unzip {project_name}.zip
2. Navigate: cd {project_name}
3. Install dependencies: npm install
4. Start dev server: npm start
5. Open browser: http://localhost:4200

The application includes:
- ✅ Modern Angular 17+ standalone components
- ✅ Reactive forms with validation
- ✅ API service pre-configured for backend
- ✅ Responsive design (mobile-first)
- ✅ Professional UI/UX
- ✅ Environment configuration
- ✅ Complete project structure
"""
        
        if stream:
            yield message
        else:
            yield message
            
    except Exception as e:
        error_msg = f"❌ Error generating frontend code: {str(e)}"
        if stream:
            yield error_msg
        else:
            yield error_msg
