import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json
import os
import zipfile
from pathlib import Path

def generate_backend_zip(backend_design: str, domain_model: str, project_name: str = "modernized-backend") -> str:
    """
    Generates a complete, deployable Spring Boot application as a zip file.
    
    Args:
        backend_design: Backend design specification
        domain_model: Domain model to generate entities
        project_name: Name of the Spring Boot project
    
    Returns:
        Path to the generated zip file
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0, max_tokens=16000)  # Increased token limit
    
    prompt = f"""
You are a senior Java Spring Boot developer. Generate a COMPLETE, PRODUCTION-READY Spring Boot 3.x application with Java 17+.

BACKEND DESIGN:
{backend_design}

DOMAIN MODEL:
{domain_model}

Generate a JSON structure with ALL files needed for a working Spring Boot app. Keep code concise and focused.

CRITICAL JSON FORMAT RULES:
1. Use escaped quotes inside JSON strings: \\" not "
2. Use \\n for newlines in code strings
3. Keep file contents under 500 lines each
4. Return ONLY valid JSON, no markdown, no code blocks

{{
  "projectName": "{project_name}",
  "groupId": "com.modernized",
  "artifactId": "{project_name}",
  "files": [
    {{
      "path": "pom.xml",
      "content": "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n<project>...</project>"
    }},
    {{
      "path": "src/main/java/com/modernized/Application.java",
      "content": "package com.modernized;\\n\\nimport org.springframework.boot.SpringApplication;\\n..."
    }}
  ]
}}

Create these essential files:
1. pom.xml - Spring Boot 3.x, JPA, Web, PostgreSQL
2. Application.java - Main class
3. One sample Entity based on domain model
4. One Repository for the entity
5. One Service for the entity  
6. One Controller for the entity
7. application.yml - Basic config
8. README.md

Keep it minimal but functional. Return ONLY the JSON structure.
"""
    
    response = llm.invoke(prompt).content
    
    # Clean up markdown code blocks if present
    response = response.replace("```json", "").replace("```", "").strip()
    
    # Try to extract JSON if there's extra text
    if not response.startswith("{"):
        # Find first { and last }
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            response = response[start:end]
    
    try:
        project_data = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON at character {e.pos}: {e.msg}")
        print(f"Context around error: {response[max(0, e.pos-100):min(len(response), e.pos+100)]}")
        # Save the problematic response for debugging
        with open("/tmp/failed_backend_response.txt", "w") as f:
            f.write(response)
        raise Exception(f"JSON parsing failed. Response saved to /tmp/failed_backend_response.txt. Error: {e}")
    
    # Create temporary directory structure
    temp_dir = Path("/tmp") / project_name
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
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
    
    print(f"✅ Backend ZIP created: {zip_path}")
    return zip_path


def backend_code_generation_agent(
    backend_design: str,
    domain_model: str,
    history: List[Dict[str, str]],
    project_name: str = "modernized-backend",
    stream: bool = False
):
    """
    Agent that generates deployable backend code.
    """
    if stream:
        yield "⚙️ Generating Spring Boot application...\n"
    
    try:
        zip_path = generate_backend_zip(backend_design, domain_model, project_name)
        
        message = f"""
✅ Backend code generated successfully!

📦 ZIP File: {zip_path}
📁 Project: {project_name}

🚀 To run:
1. unzip {project_name}.zip
2. cd {project_name}
3. mvn spring-boot:run
"""
        
        if stream:
            yield message
        else:
            return message
            
    except Exception as e:
        error_msg = f"❌ Error generating backend: {str(e)}"
        if stream:
            yield error_msg
        else:
            return error_msg
