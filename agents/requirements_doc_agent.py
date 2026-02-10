import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json

def requirements_doc_agent(vb_files: List[Dict], history: List[Dict[str, str]], stream: bool = False):
    """
    Generates a comprehensive requirements document from VB project files.
    
    Args:
        vb_files: List of dicts with 'filename' and 'content' keys
        history: Conversation history
        stream: Whether to stream the response
    
    Returns:
        JSON structure for Word document generation
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)  # Use GPT-4 for better analysis
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    # Compile all VB files into analysis
    vb_content = "\n\n".join([
        f"=== {file['filename']} ===\n{file['content']}" 
        for file in vb_files
    ])
    
    prompt = f"""
You are a business analyst converting a legacy VB application into a modern requirements document.

Conversation history:
{history_text}

Analyze these VB files and create a comprehensive requirements document structure in JSON format.

VB PROJECT FILES:
{vb_content}

Generate a JSON structure with the following format:
{{
  "projectName": "extracted from code or 'Legacy VB Application'",
  "executiveSummary": "2-3 paragraph overview of the application",
  "businessContext": {{
    "purpose": "What business problem does this solve?",
    "users": ["List of user types"],
    "keyFunctions": ["Main functions"]
  }},
  "functionalRequirements": [
    {{
      "id": "FR-001",
      "category": "User Management | Data Processing | Reporting | etc.",
      "title": "Brief title",
      "description": "Detailed description",
      "priority": "High | Medium | Low",
      "sourceCode": "Reference to VB file/function"
    }}
  ],
  "nonFunctionalRequirements": [
    {{
      "category": "Performance | Security | Scalability | etc.",
      "requirement": "Specific requirement",
      "rationale": "Why this is needed"
    }}
  ],
  "dataRequirements": {{
    "entities": [
      {{
        "name": "Entity name",
        "description": "What it represents",
        "attributes": [
          {{"name": "attr", "type": "string", "required": true, "description": "desc"}}
        ],
        "relationships": ["Related entities"]
      }}
    ]
  }},
  "userInterfaces": [
    {{
      "formName": "From VB form",
      "purpose": "What the form does",
      "controls": ["List of key controls"],
      "workflow": "User workflow description"
    }}
  ],
  "businessRules": [
    {{
      "rule": "Business rule description",
      "implementation": "How it's currently implemented",
      "validations": ["Validation logic"]
    }}
  ],
  "integrations": [
    {{
      "system": "External system name",
      "purpose": "Why integrate",
      "method": "Database | File | API | etc."
    }}
  ],
  "migrationConsiderations": {{
    "challenges": ["Identified challenges"],
    "riskAreas": ["High-risk areas"],
    "recommendations": ["Migration recommendations"]
  }}
}}

Return ONLY the JSON structure, no markdown formatting or code blocks.
"""
    
    if stream:
        full_response = ""
        for chunk in llm.stream(prompt):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            full_response += content
            yield chunk
        # After streaming completes, parse and return structured data
        # This will be picked up by the backend to generate the Word doc
    else:
        response = llm.invoke(prompt).content
        yield response
