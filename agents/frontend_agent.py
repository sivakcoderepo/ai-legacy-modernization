import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def frontend_agent(backend_design: str, history: List[Dict[str, str]], stream: bool = False):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a frontend design assistant.

Conversation history:
{history_text}

Design Angular UI components based on this backend design:

BACKEND DESIGN:
{backend_design}
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        yield llm.invoke(prompt).content
