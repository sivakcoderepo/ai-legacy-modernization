import env
from langchain_openai import ChatOpenAI
from typing import List, Dict

def legacy_code_analyzer(vb_code: str, history: List[Dict[str, str]], stream: bool = False):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    history_text = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    
    prompt = f"""
You are a legacy code assistant.

Conversation history:
{history_text}

Now analyze this VB code step by step. Focus only on business logic:

VB CODE:
{vb_code}
"""
    
    if stream:
        # Stream returns AIMessageChunk objects, yield them directly
        for chunk in llm.stream(prompt):
            yield chunk
    else:
        # Non-stream returns the full response
        yield llm.invoke(prompt).content
