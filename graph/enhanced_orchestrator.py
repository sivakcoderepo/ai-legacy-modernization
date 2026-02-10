from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from agents.requirements_doc_agent import requirements_doc_agent
from agents.legacy_analyzer import legacy_code_analyzer
from agents.domain_agent import domain_model_agent
from agents.domain_mapping_agent import domain_mapping_agent
from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from agents.cloud_agent import cloud_agent
from agents.code_generation_agent import code_generation_agent

class EnhancedState(TypedDict):
    vb_files: List[Dict]  # List of {filename, content}
    target_domain_model: str
    history: List[Dict]
    requirements_doc: str
    business_logic: str
    domain_model: str
    domain_mapping: str
    backend_design: str
    frontend_design: str
    cloud_design: str
    generated_code: str

async def modernize_stream(state: EnhancedState):
    """
    Enhanced generator that yields output for all modernization steps.
    """
    state["history"].append({"role": "user", "content": f"Analyzing {len(state['vb_files'])} VB files"})

    # 1️⃣ Requirements Document Generation
    for chunk in requirements_doc_agent(state["vb_files"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["requirements_doc"] += chunk_text
        yield {"requirements_doc": chunk_text}

    state["history"].append({"role": "assistant", "content": state["requirements_doc"]})

    # 2️⃣ Legacy Analyzer (combine all VB files)
    combined_vb = "\n\n".join([f"=== {f['filename']} ===\n{f['content']}" for f in state["vb_files"]])
    
    for chunk in legacy_code_analyzer(combined_vb, state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["business_logic"] += chunk_text
        yield {"business_logic": chunk_text}

    state["history"].append({"role": "assistant", "content": state["business_logic"]})

    # 3️⃣ Domain Model
    for chunk in domain_model_agent(state["business_logic"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["domain_model"] += chunk_text
        yield {"domain_model": chunk_text}

    state["history"].append({"role": "assistant", "content": state["domain_model"]})

    # 4️⃣ Domain Mapping (if target domain provided)
    if state.get("target_domain_model"):
        for chunk in domain_mapping_agent(
            state["domain_model"], 
            state["target_domain_model"], 
            state["history"], 
            stream=True
        ):
            chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
            state["domain_mapping"] += chunk_text
            yield {"domain_mapping": chunk_text}

        state["history"].append({"role": "assistant", "content": state["domain_mapping"]})

    # 5️⃣ Backend Design
    for chunk in backend_agent(state["domain_model"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["backend_design"] += chunk_text
        yield {"backend_design": chunk_text}

    state["history"].append({"role": "assistant", "content": state["backend_design"]})

    # 6️⃣ Frontend Design
    for chunk in frontend_agent(state["backend_design"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["frontend_design"] += chunk_text
        yield {"frontend_design": chunk_text}

    state["history"].append({"role": "assistant", "content": state["frontend_design"]})

    # 7️⃣ Cloud Design
    combined = state["backend_design"] + state["frontend_design"]
    for chunk in cloud_agent(combined, state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["cloud_design"] += chunk_text
        yield {"cloud_design": chunk_text}

    state["history"].append({"role": "assistant", "content": state["cloud_design"]})

    # 8️⃣ Code Generation
    for chunk in code_generation_agent(
        state["domain_model"],
        state["backend_design"],
        state["frontend_design"],
        state["history"],
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["generated_code"] += chunk_text
        yield {"generated_code": chunk_text}

    state["history"].append({"role": "assistant", "content": state["generated_code"]})

def build_enhanced_graph():
    graph = StateGraph(EnhancedState)
    graph.add_node("modernize_stream", modernize_stream)
    graph.set_entry_point("modernize_stream")
    graph.set_finish_point("modernize_stream")
    return graph.compile()
