import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def cloud_agent(system_design: str, history: List[Dict[str, str]]) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])

    prompt = f"""
You are a cloud deployment assistant.

Conversation history:
{history_text}

Design AWS + Docker deployment based on this system design:

SYSTEM DESIGN:
{system_design}
"""
    return llm.invoke(prompt).content
