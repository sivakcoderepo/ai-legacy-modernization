import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def backend_agent(domain_model: str, history: List[Dict[str, str]], stream: bool = False):
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)
    history_text = "\n".join(
        [f'{h["role"]}: {h["content"]}' for h in history]
    )
    prompt = f"""
You are a backend design assistant.

Conversation history:
{history_text}

Generate Spring Boot REST API using clean architecture
for the following domain:

DOMAIN MODEL:
{domain_model}
"""
    
    if stream:
        for chunk in llm.stream(prompt):
            yield chunk.content
    else:
        yield llm.invoke(prompt).content
