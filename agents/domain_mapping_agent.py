import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json

def domain_mapping_agent(source_domain: str, target_domain: str, history: List[Dict[str, str]], stream: bool = False):
    """
    Maps source domain model to target domain model and identifies gaps/transformations.
    
    Args:
        source_domain: Domain model extracted from VB code
        target_domain: Target domain model (uploaded by user or default modern structure)
        history: Conversation history
        stream: Whether to stream the response
    
    Returns:
        JSON structure with domain mappings
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a domain modeling expert. Compare these two domain models and create a comprehensive mapping.

Conversation history:
{history_text}

SOURCE DOMAIN MODEL (from legacy VB application):
{source_domain}

TARGET DOMAIN MODEL (modern architecture):
{target_domain}

Analyze and create a JSON structure with the following format:
{{
  "mappingSummary": {{
    "totalSourceEntities": 0,
    "totalTargetEntities": 0,
    "directMappings": 0,
    "transformationRequired": 0,
    "unmappedSource": 0,
    "unmappedTarget": 0,
    "overallCompatibility": "High | Medium | Low"
  }},
  "entityMappings": [
    {{
      "sourceEntity": "VB Entity Name",
      "targetEntity": "Modern Entity Name",
      "confidence": 95,
      "mappingType": "Direct | Transformation | Split | Merge",
      "propertyMappings": [
        {{
          "sourceProperty": "vb_field",
          "targetProperty": "modernField",
          "dataTypeCompatible": true,
          "transformation": null or "description of needed transformation",
          "confidence": 90
        }}
      ],
      "notes": "Any special considerations",
      "migrationComplexity": "Low | Medium | High"
    }}
  ],
  "unmappedSourceEntities": [
    {{
      "entity": "VB Entity",
      "reason": "Why it couldn't be mapped",
      "recommendation": "What to do with it"
    }}
  ],
  "unmappedTargetEntities": [
    {{
      "entity": "Modern Entity",
      "reason": "No source equivalent",
      "dataSource": "How to populate this entity"
    }}
  ],
  "transformationRules": [
    {{
      "rule": "Description of transformation",
      "sourcePattern": "What needs to change",
      "targetPattern": "What it becomes",
      "complexity": "Low | Medium | High",
      "example": "Concrete example"
    }}
  ],
  "dataQualityIssues": [
    {{
      "issue": "Problem description",
      "impact": "How it affects migration",
      "resolution": "How to fix it"
    }}
  ],
  "recommendations": [
    "Prioritized recommendations for successful migration"
  ]
}}

Return ONLY the JSON structure, no markdown formatting or code blocks.
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content
