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
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    prompt = f"""
You are a senior Angular developer. Generate a COMPLETE, PRODUCTION-READY Angular 17+ standalone application.

FRONTEND DESIGN:
{frontend_design}

DOMAIN MODEL:
{domain_model}

Generate a JSON structure with ALL files needed for a working Angular app.

CRITICAL REQUIREMENTS:

1. package.json MUST have these EXACT versions:
   - "@angular/core": "^17.3.0"
   - "zone.js": "~0.14.2"  (MUST match Angular 17.3)
   - "@angular/common": "^17.3.0"
   - All Angular packages MUST be 17.3.x

2. angular.json MUST have:
   - "browser": "src/main.ts" (NOT "main")
   - "buildTarget" (NOT "browserTarget")
   - Project name: "{project_name}"

CORRECT package.json dependencies:
{{
  "dependencies": {{
    "@angular/animations": "^17.3.0",
    "@angular/common": "^17.3.0",
    "@angular/compiler": "^17.3.0",
    "@angular/core": "^17.3.0",
    "@angular/forms": "^17.3.0",
    "@angular/platform-browser": "^17.3.0",
    "@angular/platform-browser-dynamic": "^17.3.0",
    "@angular/router": "^17.3.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.14.2"
  }},
  "devDependencies": {{
    "@angular-devkit/build-angular": "^17.3.0",
    "@angular/cli": "^17.3.0",
    "@angular/compiler-cli": "^17.3.0",
    "@types/jasmine": "~5.1.0",
    "jasmine-core": "~5.1.0",
    "karma": "~6.4.0",
    "karma-chrome-launcher": "~3.2.0",
    "karma-coverage": "~2.2.0",
    "karma-jasmine": "~5.1.0",
    "karma-jasmine-html-reporter": "~2.1.0",
    "typescript": "~5.2.2"
  }}
}}

CORRECT angular.json format:
{{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {{
    "{project_name}": {{
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
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
          }},
          "configurations": {{
            "production": {{
              "budgets": [
                {{
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                }}
              ],
              "outputHashing": "all"
            }},
            "development": {{
              "optimization": false,
              "extractLicenses": false,
              "sourceMap": true
            }}
          }},
          "defaultConfiguration": "production"
        }},
        "serve": {{
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {{
            "production": {{
              "buildTarget": "{project_name}:build:production"
            }},
            "development": {{
              "buildTarget": "{project_name}:build:development"
            }}
          }},
          "defaultConfiguration": "development"
        }}
      }}
    }}
  }},
  "cli": {{
    "analytics": false
  }}
}}

Generate complete JSON structure with these files:

{{
  "projectName": "{project_name}",
  "files": [
    {{
      "path": "package.json",
      "content": "MUST use zone.js ~0.14.2 and Angular 17.3.x"
    }},
    {{
      "path": "angular.json",
      "content": "MUST use 'browser' and 'buildTarget'"
    }},
    {{
      "path": "tsconfig.json",
      "content": "Base TypeScript config"
    }},
    {{
      "path": "tsconfig.app.json",
      "content": "App TypeScript config"
    }},
    {{
      "path": "src/main.ts",
      "content": "Bootstrap with bootstrapApplication"
    }},
    {{
      "path": "src/index.html",
      "content": "HTML with <app-root>"
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
      "path": "src/app/app.component.html",
      "content": "Root template"
    }},
    {{
      "path": "src/app/app.routes.ts",
      "content": "Application routes"
    }},
    {{
      "path": "src/app/models/[entity].model.ts",
      "content": "TypeScript interfaces from domain"
    }},
    {{
      "path": "src/app/services/[entity].service.ts",
      "content": "Services for API calls to http://localhost:8080/api"
    }},
    {{
      "path": "src/app/components/[entity]/[entity].component.ts",
      "content": "Standalone component"
    }},
    {{
      "path": "src/app/components/[entity]/[entity].component.html",
      "content": "Component template"
    }},
    {{
      "path": "src/app/components/[entity]/[entity].component.css",
      "content": "Component styles"
    }},
    {{
      "path": "README.md",
      "content": "Setup and run instructions"
    }},
    {{
      "path": ".gitignore",
      "content": "Git ignore"
    }}
  ]
}}

REQUIREMENTS:
1. Angular 17.3+ with standalone components
2. Use provideRouter, provideHttpClient
3. Reactive forms with validation
4. API URL: http://localhost:8080/api
5. TypeScript strict mode
6. Responsive design

CRITICAL: 
- zone.js MUST be ~0.14.2 (matches Angular 17.3)
- All @angular packages MUST be ^17.3.0
- angular.json MUST use "browser" not "main"

Return ONLY the JSON structure with complete code.
"""
    
    response = llm.invoke(prompt).content
    response = response.replace("```json", "").replace("```", "").strip()
    
    try:
        project_data = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        raise
    
    # FIX 1: Validate and fix angular.json
    angular_json_file = next((f for f in project_data["files"] if f["path"] == "angular.json"), None)
    if angular_json_file:
        try:
            angular_config = json.loads(angular_json_file["content"])
            if project_name in angular_config.get("projects", {}):
                build_options = angular_config["projects"][project_name]["architect"]["build"]["options"]
                if "main" in build_options and "browser" not in build_options:
                    print("⚠️ Fixing angular.json: 'main' → 'browser'")
                    build_options["browser"] = build_options.pop("main")
                    angular_json_file["content"] = json.dumps(angular_config, indent=2)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Could not validate angular.json: {e}")
    
    # FIX 2: Validate and fix package.json zone.js version
    package_json_file = next((f for f in project_data["files"] if f["path"] == "package.json"), None)
    if package_json_file:
        try:
            package_json = json.loads(package_json_file["content"])
            deps = package_json.get("dependencies", {})
            
            # Fix zone.js version
            if "zone.js" in deps and deps["zone.js"] != "~0.14.2":
                print(f"⚠️ Fixing zone.js: {deps['zone.js']} → ~0.14.2")
                deps["zone.js"] = "~0.14.2"
            
            # Ensure all Angular packages are 17.3.x
            for key in deps:
                if key.startswith("@angular/") and not deps[key].startswith("^17.3"):
                    print(f"⚠️ Fixing {key}: {deps[key]} → ^17.3.0")
                    deps[key] = "^17.3.0"
            
            # Fix devDependencies
            dev_deps = package_json.get("devDependencies", {})
            for key in dev_deps:
                if key.startswith("@angular") and not dev_deps[key].startswith("^17.3"):
                    dev_deps[key] = "^17.3.0"
            
            package_json_file["content"] = json.dumps(package_json, indent=2)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Could not validate package.json: {e}")
    
    # Create temporary directory
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
    """
    if stream:
        yield "🎨 Generating Angular 17.3 application...\n"
        yield "📦 Creating project with correct dependencies...\n"
    
    try:
        zip_path = generate_frontend_zip(frontend_design, domain_model, project_name)
        
        message = f"""
✅ Frontend code generated successfully!

📦 ZIP File: {zip_path}
📁 Project: {project_name}

🚀 To run:
1. unzip {project_name}.zip
2. cd {project_name}
3. npm install
4. npm start
5. Open http://localhost:4200

✅ Fixed versions:
- Angular: 17.3.x
- zone.js: 0.14.2
- TypeScript: 5.2.2
"""
        
        if stream:
            yield message
        else:
            yield message
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if stream:
            yield error_msg
        else:
            yield error_msg
