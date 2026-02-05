# graph/orchestrator.py

from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict

# Import all agents
from agents.legacy_analyzer import legacy_code_analyzer
from agents.domain_agent import domain_model_agent
from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from agents.cloud_agent import cloud_agent


# ---------------------------------------------------
# 1️⃣ Define Graph State
# ---------------------------------------------------

class State(TypedDict):
    vb_code: str
    history: List[Dict]
    business_logic: str
    domain_model: str
    backend_design: str
    frontend_design: str
    cloud_design: str


# ---------------------------------------------------
# 2️⃣ Node Function
# ---------------------------------------------------

def analyze(state: State) -> State:
    """
    Runs all agents sequentially and updates the state.
    """

    # Add user input to history
    state["history"].append({
        "role": "user",
        "content": state["vb_code"]
    })

    # 1️⃣ Legacy Analyzer
    logic = legacy_code_analyzer(
        state["vb_code"],
        state["history"]          # ✅ FIX
    )

    state["business_logic"] = logic
    state["history"].append({
        "role": "assistant",
        "content": logic
    })

    # 2️⃣ Domain Model
    domain = domain_model_agent(
        logic,
        state["history"]          # ✅ FIX
    )

    state["domain_model"] = domain
    state["history"].append({
        "role": "assistant",
        "content": domain
    })

    # 3️⃣ Backend Design
    backend = backend_agent(
        domain,
        state["history"]          # ✅ FIX
    )

    state["backend_design"] = backend
    state["history"].append({
        "role": "assistant",
        "content": backend
    })

    # 4️⃣ Frontend Design
    frontend = frontend_agent(
        backend,
        state["history"]          # ✅ FIX
    )

    state["frontend_design"] = frontend
    state["history"].append({
        "role": "assistant",
        "content": frontend
    })

    # 5️⃣ Cloud Design
    cloud = cloud_agent(
        backend + frontend,
        state["history"]          # ✅ FIX
    )

    state["cloud_design"] = cloud
    state["history"].append({
        "role": "assistant",
        "content": cloud
    })

    return state


# ---------------------------------------------------
# 3️⃣ Build Graph
# ---------------------------------------------------

def build_graph():
    """
    Creates and compiles the LangGraph workflow.
    """

    graph = StateGraph(State)

    graph.add_node("analyze", analyze)
    graph.set_entry_point("analyze")
    graph.set_finish_point("analyze")

    compiled_graph = graph.compile()

    return compiled_graph


# ---------------------------------------------------
# 4️⃣ Execution Helper (Used by FastAPI)
# ---------------------------------------------------

def run_graph(initial_state: dict):
    """
    Wrapper used by API layer.
    Executes compiled graph correctly.
    """

    graph = build_graph()

    # ✅ Correct method for langgraph 1.0.5
    result = graph.invoke(initial_state)

    return result
