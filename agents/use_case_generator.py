import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json

def use_case_generator_agent(
    requirements_doc: str,
    business_logic: str,
    history: List[Dict[str, str]],
    stream: bool = False
):
    """
    Generates comprehensive use cases from business requirements and logic.
    
    Args:
        requirements_doc: Requirements document content
        business_logic: Analyzed business logic
        history: Conversation history
        stream: Whether to stream the response
    
    Returns:
        Structured use case document
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a business analyst creating detailed use cases from requirements and business logic.

Conversation history:
{history_text}

REQUIREMENTS DOCUMENT:
{requirements_doc}

BUSINESS LOGIC:
{business_logic}

Generate a comprehensive use case document in the following JSON structure:

{{
  "projectName": "Application Name",
  "useCaseOverview": {{
    "purpose": "Overall purpose of the system",
    "scope": "What is covered by these use cases",
    "actors": [
      {{
        "name": "User Type",
        "description": "Who they are",
        "responsibilities": ["What they can do"]
      }}
    ]
  }},
  "useCases": [
    {{
      "id": "UC-001",
      "title": "Use Case Title",
      "priority": "High | Medium | Low",
      "actors": ["Primary Actor", "Secondary Actor"],
      "preconditions": [
        "Condition that must be true before use case executes"
      ],
      "postconditions": [
        "State after successful execution"
      ],
      "mainFlow": [
        {{
          "step": 1,
          "actor": "User",
          "action": "Action performed",
          "system": "System response"
        }}
      ],
      "alternativeFlows": [
        {{
          "name": "Alternative Flow Name",
          "condition": "When this occurs",
          "steps": [
            {{
              "step": "1a",
              "description": "What happens"
            }}
          ]
        }}
      ],
      "exceptionFlows": [
        {{
          "name": "Exception Name",
          "condition": "Error condition",
          "handling": "How system handles it"
        }}
      ],
      "businessRules": [
        "Business rule that applies to this use case"
      ],
      "uiRequirements": [
        "UI element or screen needed"
      ],
      "dataRequirements": [
        "Data needed for this use case"
      ],
      "nonFunctionalRequirements": [
        "Performance, security, etc."
      ],
      "relatedUseCases": [
        {{
          "id": "UC-002",
          "relationship": "extends | includes | precedes"
        }}
      ],
      "testScenarios": [
        {{
          "scenario": "Test scenario description",
          "expectedResult": "What should happen"
        }}
      ]
    }}
  ],
  "useCaseDiagram": "PlantUML or Mermaid syntax for use case diagram",
  "traceabilityMatrix": [
    {{
      "requirementId": "FR-001",
      "useCaseIds": ["UC-001", "UC-003"],
      "coverage": "How requirement is covered"
    }}
  ]
}}

REQUIREMENTS:
1. Create use cases for ALL major functionality
2. Include happy path AND error scenarios
3. Map use cases to requirements
4. Include UI mockup descriptions
5. Add validation rules
6. Specify data flow
7. Include security considerations
8. Add performance requirements
9. Create test scenarios
10. Make it actionable for developers

Aim for 5-15 detailed use cases covering all core functionality.

Return ONLY the JSON structure.
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content


def generate_use_case_document(use_cases_json: str, output_format: str = "markdown") -> str:
    """
    Converts use case JSON to a formatted document.
    
    Args:
        use_cases_json: JSON string with use cases
        output_format: "markdown" or "html"
    
    Returns:
        Formatted document string
    """
    try:
        use_cases = json.loads(use_cases_json)
    except json.JSONDecodeError:
        # Clean up markdown code blocks
        use_cases_json = use_cases_json.replace("```json", "").replace("```", "").strip()
        use_cases = json.loads(use_cases_json)
    
    if output_format == "markdown":
        doc = f"""# Use Case Document: {use_cases['projectName']}

## Overview

**Purpose:** {use_cases['useCaseOverview']['purpose']}

**Scope:** {use_cases['useCaseOverview']['scope']}

## Actors

"""
        for actor in use_cases['useCaseOverview']['actors']:
            doc += f"### {actor['name']}\n"
            doc += f"{actor['description']}\n\n"
            doc += "**Responsibilities:**\n"
            for resp in actor['responsibilities']:
                doc += f"- {resp}\n"
            doc += "\n"
        
        doc += "## Use Cases\n\n"
        
        for uc in use_cases['useCases']:
            doc += f"### {uc['id']}: {uc['title']}\n\n"
            doc += f"**Priority:** {uc['priority']}  \n"
            doc += f"**Actors:** {', '.join(uc['actors'])}  \n\n"
            
            doc += "**Preconditions:**\n"
            for pre in uc['preconditions']:
                doc += f"- {pre}\n"
            doc += "\n"
            
            doc += "**Postconditions:**\n"
            for post in uc['postconditions']:
                doc += f"- {post}\n"
            doc += "\n"
            
            doc += "**Main Flow:**\n\n"
            doc += "| Step | Actor | Action | System Response |\n"
            doc += "|------|-------|--------|----------------|\n"
            for step in uc['mainFlow']:
                doc += f"| {step['step']} | {step['actor']} | {step['action']} | {step['system']} |\n"
            doc += "\n"
            
            if uc.get('alternativeFlows'):
                doc += "**Alternative Flows:**\n\n"
                for alt in uc['alternativeFlows']:
                    doc += f"- **{alt['name']}**: {alt['condition']}\n"
            
            if uc.get('exceptionFlows'):
                doc += "\n**Exception Flows:**\n\n"
                for exc in uc['exceptionFlows']:
                    doc += f"- **{exc['name']}**: {exc['condition']} → {exc['handling']}\n"
            
            doc += "\n---\n\n"
        
        return doc
    
    return use_cases_json
