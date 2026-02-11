import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def use_case_generator_agent(
    requirements_doc: str,
    business_logic: str,
    history: List[Dict[str, str]],
    stream: bool = False
):
    """
    Generates comprehensive use cases in Gherkin (BDD) format from business requirements and logic.
    """
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a business analyst creating detailed use cases in Gherkin (BDD) format.

Conversation history:
{history_text}

REQUIREMENTS DOCUMENT:
{requirements_doc}

BUSINESS LOGIC:
{business_logic}

Generate comprehensive use cases in Gherkin format (Behavior Driven Development).

Format each use case as follows:

Feature: [Feature Name]
  As a [role]
  I want [feature]
  So that [benefit]

  Background:
    Given [common precondition]
    And [another common precondition]

  Scenario: [Scenario Name]
    Given [initial context]
    And [additional context]
    When [action taken]
    And [another action]
    Then [expected outcome]
    And [another outcome]

  Scenario Outline: [Scenario with examples]
    Given [parameterized context]
    When [parameterized action]
    Then [parameterized outcome]
    
    Examples:
      | parameter1 | parameter2 | expected_result |
      | value1     | value2     | result1         |
      | value3     | value4     | result2         |

Create 5-10 comprehensive features covering all major functionality.
Each feature should have:
- Clear business value statement
- Background with common setup
- 3-5 scenarios per feature
- At least one scenario outline with examples
- Both happy path and error scenarios

Return the use cases in plain Gherkin text format.
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content
