import env
from langchain_openai import ChatOpenAI
from typing import List,Dict

def domain_model_agent(business_logic: str, history: List[Dict[str,str]]) -> str:

    llm = ChatOpenAI(model="gpt-4.1", temperature=0)    
    history_text="\n".join(
        [f'{h["role"]}:{h["content"]}' for h in history]
    )
    prompt = f"""
    You are a domain model assistant.

    Conversation history:
    {history_text}

    Extract domain entities, bounded contexts, and business rules
    from the following description:

    BUSINESS LOGIC:
    {business_logic}
    """
    return llm.invoke(prompt).content
