import env
from langchain_openai import ChatOpenAI
from typing import List, Dict
import json

def domain_model_agent(business_logic: str, history: List[Dict[str, str]], stream: bool = False):
    """
    Domain model extraction agent - outputs structured JSON format.
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a domain modeling expert using Domain-Driven Design (DDD) principles.

Conversation history:
{history_text}

Extract domain entities, bounded contexts, and business rules from the following business logic:

BUSINESS LOGIC:
{business_logic}

Generate a STRUCTURED JSON domain model with the following format:

{{
  "boundedContexts": [
    {{
      "name": "Context Name",
      "description": "What this context handles",
      "entities": ["Entity1", "Entity2"]
    }}
  ],
  "entities": [
    {{
      "name": "EntityName",
      "description": "What this entity represents",
      "boundedContext": "Which context it belongs to",
      "attributes": [
        {{
          "name": "attributeName",
          "type": "string | number | boolean | Date",
          "required": true,
          "description": "What this attribute represents"
        }}
      ],
      "relationships": [
        {{
          "type": "OneToMany | ManyToOne | ManyToMany | OneToOne",
          "target": "TargetEntityName",
          "description": "Relationship description"
        }}
      ],
      "businessRules": [
        "Rule 1: Description",
        "Rule 2: Description"
      ]
    }}
  ],
  "valueObjects": [
    {{
      "name": "ValueObjectName",
      "description": "Immutable value object",
      "attributes": [
        {{
          "name": "attributeName",
          "type": "string",
          "required": true
        }}
      ]
    }}
  ],
  "aggregates": [
    {{
      "name": "AggregateName",
      "rootEntity": "EntityName",
      "entities": ["Entity1", "Entity2"],
      "description": "Aggregate boundary and purpose"
    }}
  ],
  "domainEvents": [
    {{
      "name": "EventName",
      "trigger": "What triggers this event",
      "data": ["field1", "field2"]
    }}
  ]
}}

Return ONLY the JSON structure, no markdown code blocks, no additional text.
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content
