from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from agents.legacy_analyzer import legacy_code_analyzer
from agents.domain_agent import domain_model_agent
from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from agents.cloud_agent import cloud_agent

class State(TypedDict):
    vb_code: str
    history: List[Dict]
    business_logic: str
    domain_model: str
    backend_design: str
    frontend_design: str
    cloud_design: str

# -----------------------------
# Streaming Node
# -----------------------------
async def analyze_stream(state: State):
    """
    Async generator that yields each agent output for streaming.
    """
    state["history"].append({"role": "user", "content": state["vb_code"]})

    # 1️⃣ Legacy Analyzer
    for chunk in legacy_code_analyzer(state["vb_code"], state["history"], stream=True):
        state["business_logic"] += chunk
        yield {"agent": "business_logic", "output": chunk}

    state["history"].append({"role": "assistant", "content": state["business_logic"]})

    # 2️⃣ Domain Model
    for chunk in domain_model_agent(state["business_logic"], state["history"], stream=True):
        state["domain_model"] += chunk
        yield {"agent": "domain_model", "output": chunk}

    state["history"].append({"role": "assistant", "content": state["domain_model"]})

    # 3️⃣ Backend Design
    for chunk in backend_agent(state["domain_model"], state["history"], stream=True):
        state["backend_design"] += chunk
        yield {"agent": "backend_design", "output": chunk}

    state["history"].append({"role": "assistant", "content": state["backend_design"]})

    # 4️⃣ Frontend Design
    for chunk in frontend_agent(state["backend_design"], state["history"], stream=True):
        state["frontend_design"] += chunk
        yield {"agent": "frontend_design", "output": chunk}

    state["history"].append({"role": "assistant", "content": state["frontend_design"]})

    # 5️⃣ Cloud Design
    combined = state["backend_design"] + state["frontend_design"]
    for chunk in cloud_agent(combined, state["history"], stream=True):
        state["cloud_design"] += chunk
        yield {"agent": "cloud_design", "output": chunk}

    state["history"].append({"role": "assistant", "content": state["cloud_design"]})

# -----------------------------
# Build Graph
# -----------------------------
def build_graph():
    graph = StateGraph(State)
    graph.add_node("analyze_stream", analyze_stream)
    graph.set_entry_point("analyze_stream")
    graph.set_finish_point("analyze_stream")
    return graph.compile()
