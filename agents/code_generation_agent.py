import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json

def code_generation_agent(
    domain_model: str,
    backend_design: str,
    frontend_design: str,
    history: List[Dict[str, str]],
    stream: bool = False
):
    """
    Generates complete, deployable Spring Boot and Angular code.
    
    Args:
        domain_model: Domain model
        backend_design: Backend architecture design
        frontend_design: Frontend design
        history: Conversation history
        stream: Whether to stream the response
    
    Returns:
        JSON structure with complete code files
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0,  request_timeout=120,  # 2 minutes
    max_retries=3)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a senior full-stack developer. Generate complete, production-ready code for both backend and frontend.

Conversation history:
{history_text}

DOMAIN MODEL:
{domain_model}

BACKEND DESIGN:
{backend_design}

FRONTEND DESIGN:
{frontend_design}

Generate a comprehensive JSON structure with ALL code files needed for deployment:

{{
  "backend": {{
    "entities": [
      {{
        "path": "src/main/java/com/example/domain/entity",
        "filename": "EntityName.java",
        "content": "complete Java code with JPA annotations"
      }}
    ],
    "repositories": [
      {{
        "path": "src/main/java/com/example/infrastructure/repository",
        "filename": "EntityNameRepository.java",
        "content": "Spring Data JPA repository interface"
      }}
    ],
    "services": [
      {{
        "path": "src/main/java/com/example/application/service",
        "filename": "EntityNameService.java",
        "content": "Service interface"
      }},
      {{
        "path": "src/main/java/com/example/application/service/impl",
        "filename": "EntityNameServiceImpl.java",
        "content": "Service implementation"
      }}
    ],
    "controllers": [
      {{
        "path": "src/main/java/com/example/interfaces/rest",
        "filename": "EntityNameController.java",
        "content": "REST controller with all CRUD endpoints"
      }}
    ],
    "dtos": [
      {{
        "path": "src/main/java/com/example/interfaces/dto",
        "filename": "EntityNameDTO.java",
        "content": "DTO classes"
      }}
    ],
    "config": [
      {{
        "path": "src/main/java/com/example/config",
        "filename": "DatabaseConfig.java",
        "content": "Database configuration"
      }},
      {{
        "path": "src/main/java/com/example/config",
        "filename": "SecurityConfig.java",
        "content": "Spring Security configuration"
      }},
      {{
        "path": "src/main/java/com/example/config",
        "filename": "CorsConfig.java",
        "content": "CORS configuration"
      }}
    ],
    "application": {{
      "path": "src/main/java/com/example",
      "filename": "Application.java",
      "content": "Spring Boot main class"
    }},
    "resources": [
      {{
        "path": "src/main/resources",
        "filename": "application.yml",
        "content": "Spring Boot configuration"
      }},
      {{
        "path": "src/main/resources",
        "filename": "application-dev.yml",
        "content": "Dev profile configuration"
      }},
      {{
        "path": "src/main/resources",
        "filename": "application-prod.yml",
        "content": "Production profile configuration"
      }}
    ],
    "pom": "complete pom.xml with all dependencies"
  }},
  "frontend": {{
    "components": [
      {{
        "path": "src/app/components/entity-name",
        "filename": "entity-name.component.ts",
        "content": "Angular component TypeScript"
      }},
      {{
        "path": "src/app/components/entity-name",
        "filename": "entity-name.component.html",
        "content": "Angular component HTML template"
      }},
      {{
        "path": "src/app/components/entity-name",
        "filename": "entity-name.component.css",
        "content": "Component styles"
      }}
    ],
    "services": [
      {{
        "path": "src/app/services",
        "filename": "entity-name.service.ts",
        "content": "Angular service for API calls"
      }}
    ],
    "models": [
      {{
        "path": "src/app/models",
        "filename": "entity-name.model.ts",
        "content": "TypeScript interfaces/models"
      }}
    ],
    "routing": [
      {{
        "path": "src/app",
        "filename": "app.routes.ts",
        "content": "Angular routing configuration"
      }}
    ],
    "app": {{
      "path": "src/app",
      "filename": "app.component.ts",
      "content": "Root component"
    }},
    "packageJson": "complete package.json with all dependencies",
    "angularJson": "angular.json configuration",
    "tsconfig": "tsconfig.json"
  }},
  "deployment": {{
    "dockerfile_backend": "Dockerfile for Spring Boot",
    "dockerfile_frontend": "Dockerfile for Angular",
    "dockerCompose": "docker-compose.yml for both services + database",
    "kubernetes": [
      {{
        "filename": "backend-deployment.yaml",
        "content": "Kubernetes deployment for backend"
      }},
      {{
        "filename": "frontend-deployment.yaml",
        "content": "Kubernetes deployment for frontend"
      }},
      {{
        "filename": "database-deployment.yaml",
        "content": "Kubernetes deployment for PostgreSQL"
      }},
      {{
        "filename": "ingress.yaml",
        "content": "Ingress configuration"
      }}
    ],
    "cicd": [
      {{
        "filename": ".github/workflows/backend-ci.yml",
        "content": "GitHub Actions for backend"
      }},
      {{
        "filename": ".github/workflows/frontend-ci.yml",
        "content": "GitHub Actions for frontend"
      }}
    ]
  }},
  "scripts": [
    {{
      "filename": "build-all.sh",
      "content": "Script to build both backend and frontend"
    }},
    {{
      "filename": "deploy-local.sh",
      "content": "Script to deploy locally with Docker Compose"
    }},
    {{
      "filename": "README.md",
      "content": "Complete README with setup instructions"
    }}
  ]
}}

REQUIREMENTS:
1. Use Spring Boot 3.x with Java 17+
2. Use Angular 17+ with standalone components
3. Include proper error handling, validation, and logging
4. Add Swagger/OpenAPI documentation
5. Include database migration scripts (Flyway or Liquibase)
6. Add comprehensive unit tests for critical services
7. Use DTOs to separate domain models from API contracts
8. Implement proper REST API design (HATEOAS where appropriate)
9. Add health check endpoints
10. Include environment-specific configurations

Return ONLY the JSON structure with complete, deployable code.
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content
