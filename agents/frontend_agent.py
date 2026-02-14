import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def frontend_agent(backend_design: str, history: List[Dict[str, str]], stream: bool = False):
    """
    Frontend design assistant that creates Angular UI component specifications
    with TypeScript safety in mind.
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a senior Angular UI/UX architect with expertise in TypeScript strict mode and modern Angular patterns.

Conversation history:
{history_text}

Design Angular 17+ UI components based on this backend design:

BACKEND DESIGN:
{backend_design}

Create a comprehensive frontend design specification that includes:

1. COMPONENT ARCHITECTURE
   - List all Angular standalone components needed
   - Component hierarchy and routing structure
   - Shared components and utilities
   - Service dependencies for each component

2. FORMS & VALIDATION
   - Reactive Forms with FormBuilder
   - Validation rules for each field
   - Error messages and user feedback
   - Form submission flows

3. DATA FLOW
   - How data flows from API to UI
   - State management approach (services with BehaviorSubject)
   - Real-time updates and subscriptions
   - Error handling strategies

4. UI/UX PATTERNS
   - Navigation structure (header, sidebar, etc.)
   - List views with search/filter/pagination
   - Detail/edit views with form validation
   - Loading states and error displays
   - Responsive design considerations

5. TYPESCRIPT SAFETY REQUIREMENTS
   - All form values must use null coalescing (??)
   - All services must have public getter methods
   - All form controls must have safe access patterns
   - All API responses must have explicit types

6. ACCESSIBILITY & BEST PRACTICES
   - ARIA labels for form controls
   - Keyboard navigation support
   - Responsive breakpoints
   - Loading indicators and error messages

For each component, specify:
- Component name and purpose
- Template structure (HTML layout)
- Form fields (if applicable) with validation
- Service methods it uses
- Routing parameters
- Input/Output properties

Example component spec format:

```
Component: PropertyListComponent
Purpose: Display paginated list of properties with search
Template:
  - Search bar (filter by name, type)
  - Data table with columns: name, address, type, units, price
  - Pagination controls
  - "Add New" button
Form: Search form with reactive validation
Services: PropertyService (getAll, delete)
Routes: /properties
Features:
  - Client-side filtering
  - Sort by column headers
  - Delete confirmation dialog
  - Navigate to detail on row click
```

Provide complete specifications for all components needed to implement the backend design.

CRITICAL: Design with TypeScript strict mode in mind:
- All nullable values need default values or null checks
- All form accesses need safe navigation
- All service calls need error handling
- All subscriptions need proper cleanup
"""
    
    if stream:
        response = ""
        for chunk in llm.stream(prompt):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            response += content
            yield content
    else:
        response = llm.invoke(prompt).content
        yield response