import env

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1", temperature=0)

def legacy_code_analyzer(vb_code: str,history: list) -> str:
    llm = ChatOpenAI(model="gpt-4.1",temperature=0)
    history_text="\n".join(
        [f'{h["role"]}:{h["content"]}' for h in history]
    )
    prompt = f"""
    You are a legacy code assistant.

    Converstation history:
    {history_text}

    Now analyze this VB code step by step.Focus only on business logic:

    VB CODE:
    {vb_code}
    """
    return llm.invoke(prompt).content
