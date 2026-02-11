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
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""
You are a senior Angular developer. Generate a COMPLETE, PRODUCTION-READY Angular 17+ standalone application.

FRONTEND DESIGN:
{frontend_design}

DOMAIN MODEL:
{domain_model}

Generate a JSON structure with ALL files needed for a working Angular app that can be deployed immediately.

CRITICAL REQUIREMENTS FOR angular.json:
1. Project name MUST be "{project_name}"
2. Build options MUST include "browser": "src/main.ts" (NOT "main")
3. Serve configuration MUST use "buildTarget" (NOT "browserTarget")
4. NO "defaultProject" property (deprecated)
5. Use Angular 17+ format

CORRECT angular.json format:
{{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "projects": {{
    "{project_name}": {{
      "architect": {{
        "build": {{
          "builder": "@angular-devkit/build-angular:browser",
          "options": {{
            "outputPath": "dist/{project_name}",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.css"],
            "scripts": []
          }}
        }},
        "serve": {{
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {{
            "development": {{
              "buildTarget": "{project_name}:build:development"
            }}
          }},
          "defaultConfiguration": "development"
        }}
      }}
    }}
  }}
}}

Generate complete JSON structure with these files:

{{
  "projectName": "{project_name}",
  "files": [
    {{
      "path": "package.json",
      "content": "Complete package.json with Angular 17+ dependencies"
    }},
    {{
      "path": "angular.json",
      "content": "MUST follow the CORRECT format above with 'browser' property"
    }},
    {{
      "path": "tsconfig.json",
      "content": "TypeScript base configuration"
    }},
    {{
      "path": "tsconfig.app.json",
      "content": "Application TypeScript configuration"
    }},
    {{
      "path": "src/main.ts",
      "content": "Bootstrap file with bootstrapApplication"
    }},
    {{
      "path": "src/index.html",
      "content": "HTML shell with <app-root>"
    }},
    {{
      "path": "src/styles.css",
      "content": "Global styles"
    }},
    {{
      "path": "src/app/app.component.ts",
      "content": "Root standalone component"
    }},
    {{
      "path": "src/app/app.routes.ts",
      "content": "Application routes"
    }},
    {{
      "path": "src/app/models/[MODEL_NAME].model.ts",
      "content": "TypeScript interfaces from domain model"
    }},
    {{
      "path": "src/app/services/[SERVICE_NAME].service.ts",
      "content": "Injectable services for API calls"
    }},
    {{
      "path": "src/app/components/[COMPONENT_NAME]/[COMPONENT_NAME].component.ts",
      "content": "Standalone component TypeScript"
    }},
    {{
      "path": "src/app/components/[COMPONENT_NAME]/[COMPONENT_NAME].component.html",
      "content": "Component HTML template"
    }},
    {{
      "path": "src/app/components/[COMPONENT_NAME]/[COMPONENT_NAME].component.css",
      "content": "Component styles"
    }},
    {{
      "path": "README.md",
      "content": "Complete setup and run instructions"
    }},
    {{
      "path": ".gitignore",
      "content": "Git ignore for Angular projects"
    }},
    {{
      "path": "Dockerfile",
      "content": "Multi-stage Dockerfile for production"
    }}
  ]
}}

REQUIREMENTS:
1. Angular 17+ with standalone components (NO NgModule)
2. Use provideRouter for routing
3. Use provideHttpClient for HTTP
4. Reactive forms with FormsModule
5. CommonModule for directives
6. API base URL: http://localhost:8080/api
7. Responsive design with CSS Grid/Flexbox
8. Form validation
9. Error handling
10. Loading states
11. TypeScript strict mode
12. Production build optimization
13. Docker support

For [MODEL_NAME], [SERVICE_NAME], [COMPONENT_NAME] placeholders, create files for EACH entity in the domain model.

CRITICAL: Ensure angular.json uses "browser" NOT "main", and "buildTarget" NOT "browserTarget"

Return ONLY the JSON structure with complete, working code.
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
    
    # Validate angular.json has correct format
    angular_json_file = next((f for f in project_data["files"] if f["path"] == "angular.json"), None)
    if angular_json_file:
        try:
            angular_config = json.loads(angular_json_file["content"])
            # Check if it has the correct 'browser' property
            if project_name in angular_config.get("projects", {}):
                build_options = angular_config["projects"][project_name]["architect"]["build"]["options"]
                if "main" in build_options and "browser" not in build_options:
                    # Fix it: rename 'main' to 'browser'
                    print("⚠️ Fixing angular.json: changing 'main' to 'browser'")
                    build_options["browser"] = build_options.pop("main")
                    angular_json_file["content"] = json.dumps(angular_config, indent=2)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Could not validate angular.json: {e}")
    
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
        yield "🎨 Generating complete Angular 17+ application...\n"
        yield "📦 Creating project structure with standalone components...\n"
    
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
- ✅ Angular 17+ with standalone components
- ✅ TypeScript strict mode
- ✅ Reactive forms with validation
- ✅ HTTP client configured for API
- ✅ Routing with lazy loading
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Docker support
- ✅ Production build ready
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