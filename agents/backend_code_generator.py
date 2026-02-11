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
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""
You are a senior Java Spring Boot developer. Generate a COMPLETE, PRODUCTION-READY Spring Boot 3.x application with Java 17+.

BACKEND DESIGN:
{backend_design}

DOMAIN MODEL:
{domain_model}

Generate a JSON structure with ALL files needed for a working Spring Boot app that can be deployed immediately:

{{
  "projectName": "{project_name}",
  "groupId": "com.modernized",
  "artifactId": "{project_name}",
  "files": [
    {{
      "path": "pom.xml",
      "content": "Complete pom.xml with Spring Boot 3.x, JPA, Web, Security, Validation, PostgreSQL driver"
    }},
    {{
      "path": "src/main/java/com/modernized/application/Application.java",
      "content": "Spring Boot main application class with @SpringBootApplication"
    }},
    {{
      "path": "src/main/java/com/modernized/domain/entity/BaseEntity.java",
      "content": "Base entity class with id, createdAt, updatedAt"
    }},
    {{
      "path": "src/main/java/com/modernized/domain/entity/[ENTITY_NAME].java",
      "content": "JPA entity classes for each domain entity with proper annotations"
    }},
    {{
      "path": "src/main/java/com/modernized/domain/repository/[ENTITY_NAME]Repository.java",
      "content": "Spring Data JPA repository interfaces"
    }},
    {{
      "path": "src/main/java/com/modernized/application/service/[ENTITY_NAME]Service.java",
      "content": "Service interface"
    }},
    {{
      "path": "src/main/java/com/modernized/application/service/impl/[ENTITY_NAME]ServiceImpl.java",
      "content": "Service implementation with business logic"
    }},
    {{
      "path": "src/main/java/com/modernized/interfaces/rest/[ENTITY_NAME]Controller.java",
      "content": "REST controller with CRUD endpoints, proper validation, error handling"
    }},
    {{
      "path": "src/main/java/com/modernized/interfaces/dto/[ENTITY_NAME]DTO.java",
      "content": "DTO classes with validation annotations"
    }},
    {{
      "path": "src/main/java/com/modernized/interfaces/dto/ErrorResponse.java",
      "content": "Standard error response DTO"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/config/DatabaseConfig.java",
      "content": "Database configuration"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/config/SecurityConfig.java",
      "content": "Spring Security configuration with CORS, JWT ready"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/config/WebConfig.java",
      "content": "Web MVC configuration"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/exception/GlobalExceptionHandler.java",
      "content": "Global exception handler with @RestControllerAdvice"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/exception/ResourceNotFoundException.java",
      "content": "Custom exception for not found resources"
    }},
    {{
      "path": "src/main/java/com/modernized/infrastructure/exception/ValidationException.java",
      "content": "Custom validation exception"
    }},
    {{
      "path": "src/main/resources/application.yml",
      "content": "Main application properties with database config, server port 8080"
    }},
    {{
      "path": "src/main/resources/application-dev.yml",
      "content": "Development profile configuration"
    }},
    {{
      "path": "src/main/resources/application-prod.yml",
      "content": "Production profile configuration"
    }},
    {{
      "path": "src/main/resources/db/migration/V1__initial_schema.sql",
      "content": "Flyway migration script for initial database schema"
    }},
    {{
      "path": "src/test/java/com/modernized/application/service/[ENTITY_NAME]ServiceTest.java",
      "content": "Unit tests for service layer"
    }},
    {{
      "path": ".gitignore",
      "content": "Git ignore file for Java/Maven projects"
    }},
    {{
      "path": "README.md",
      "content": "Complete README with setup, API documentation, and deployment instructions"
    }},
    {{
      "path": "Dockerfile",
      "content": "Multi-stage Dockerfile for production deployment"
    }},
    {{
      "path": "docker-compose.yml",
      "content": "Docker compose with Spring Boot app and PostgreSQL database"
    }}
  ]
}}

REQUIREMENTS:
1. Use Spring Boot 3.x with Java 17+
2. Clean architecture: domain, application, infrastructure, interfaces layers
3. JPA entities with proper relationships
4. DTOs separate from entities
5. Comprehensive error handling
6. Input validation with @Valid
7. CORS configured for frontend
8. Swagger/OpenAPI documentation
9. Database migrations with Flyway
10. Health check endpoint
11. Logging configuration
12. Unit tests for critical services
13. Docker support
14. Production-ready configuration

Database: PostgreSQL
Port: 8080
API Base Path: /api

For [ENTITY_NAME] placeholders, create files for EACH entity in the domain model.

Return ONLY the JSON structure with complete, compilable code.
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


def backend_code_generation_agent(
    backend_design: str,
    domain_model: str,
    history: List[Dict[str, str]],
    project_name: str = "modernized-backend",
    stream: bool = False
):
    """
    Agent that generates deployable backend code.
    
    Args:
        backend_design: Backend design specification
        domain_model: Domain model
        history: Conversation history
        project_name: Name of the project
        stream: Whether to stream the response
    
    Yields:
        Status updates and final zip file path
    """
    if stream:
        yield "⚙️ Generating complete Spring Boot application...\n"
        yield "📦 Creating project structure...\n"
    
    try:
        zip_path = generate_backend_zip(backend_design, domain_model, project_name)
        
        message = f"""
✅ Backend code generated successfully!

📦 ZIP File: {zip_path}
📁 Project Name: {project_name}

🚀 To run the application:
1. Unzip the file: unzip {project_name}.zip
2. Navigate: cd {project_name}
3. Start PostgreSQL: docker-compose up -d postgres
4. Build: ./mvnw clean install
5. Run: ./mvnw spring-boot:run
6. API available at: http://localhost:8080/api

The application includes:
- ✅ Spring Boot 3.x with Java 17+
- ✅ Clean architecture (4 layers)
- ✅ JPA entities with relationships
- ✅ REST API with full CRUD
- ✅ Validation and error handling
- ✅ PostgreSQL database
- ✅ Flyway migrations
- ✅ Docker support
- ✅ Swagger documentation
- ✅ Unit tests
- ✅ Production-ready configuration
"""
        
        if stream:
            yield message
        else:
            yield message
            
    except Exception as e:
        error_msg = f"❌ Error generating backend code: {str(e)}"
        if stream:
            yield error_msg
        else:
            yield error_msg
