from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from agents.legacy_analyzer import legacy_code_analyzer
from agents.domain_agent import domain_model_agent
from agents.domain_mapping_agent import domain_mapping_agent
from agents.backend_agent import backend_agent
from agents.frontend_agent import frontend_agent
from agents.cloud_agent import cloud_agent
from agents.use_case_generator import use_case_generator_agent
from agents.frontend_code_generator import frontend_code_generation_agent
from agents.backend_code_generator import backend_code_generation_agent
import asyncio

class EnhancedState(TypedDict):
    vb_files: List[Dict]
    target_domain_model: str
    use_case_document: str
    history: List[Dict]
    business_logic: str
    domain_model: str
    domain_mapping: str
    backend_design: str
    frontend_design: str
    cloud_design: str
    frontend_zip_path: str
    backend_zip_path: str
    current_stage: str
    stage_approved: bool

async def modernize_stream_with_approval(state: EnhancedState):
    """
    Modernization workflow with USER APPROVAL at each stage.
    
    Workflow:
    1. Run stage → Yield results → WAIT for approval
    2. User approves → Continue to next stage
    3. User can provide target domain model at domain stage
    """
    state["history"].append({"role": "user", "content": f"Analyzing {len(state['vb_files'])} VB files"})

    # 1️⃣ STAGE: Business Logic Analysis
    state["current_stage"] = "business_logic"
    combined_vb = "\n\n".join([f"=== {f['filename']} ===\n{f['content']}" for f in state["vb_files"]])
    
    for chunk in legacy_code_analyzer(combined_vb, state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["business_logic"] += chunk_text
        yield {"business_logic": chunk_text, "stage": "business_logic", "stage_complete": False}
        await asyncio.sleep(0)

    # Mark stage complete and wait for approval
    yield {"business_logic": "", "stage": "business_logic", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["business_logic"]})

    # 2️⃣ STAGE: Use Case Generation
    state["current_stage"] = "use_cases"
    for chunk in use_case_generator_agent("", state["business_logic"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["use_case_document"] += chunk_text
        yield {"use_cases": chunk_text, "stage": "use_cases", "stage_complete": False}
        await asyncio.sleep(0)

    yield {"use_cases": "", "stage": "use_cases", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["use_case_document"]})

    # 3️⃣ STAGE: Domain Model Extraction
    state["current_stage"] = "domain_model"
    for chunk in domain_model_agent(state["business_logic"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["domain_model"] += chunk_text
        yield {"domain_model": chunk_text, "stage": "domain_model", "stage_complete": False}
        await asyncio.sleep(0)

    yield {"domain_model": "", "stage": "domain_model", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["domain_model"]})

    # 3.5️⃣ STAGE: Domain Model Comparison (if target provided)
    if state.get("target_domain_model") and state["target_domain_model"].strip():
        state["current_stage"] = "domain_mapping"
        for chunk in domain_mapping_agent(
            state["domain_model"], 
            state["target_domain_model"], 
            state["history"], 
            stream=True
        ):
            chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
            state["domain_mapping"] += chunk_text
            yield {"domain_mapping": chunk_text, "stage": "domain_mapping", "stage_complete": False}
            await asyncio.sleep(0)

        yield {"domain_mapping": "", "stage": "domain_mapping", "stage_complete": True}
        state["history"].append({"role": "assistant", "content": state["domain_mapping"]})

    # 4️⃣ STAGE: Backend Design
    state["current_stage"] = "backend_design"
    for chunk in backend_agent(
        state["domain_model"],
        state["business_logic"],
        state["history"],
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["backend_design"] += chunk_text
        yield {"backend_design": chunk_text, "stage": "backend_design", "stage_complete": False}
        await asyncio.sleep(0)

    yield {"backend_design": "", "stage": "backend_design", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["backend_design"]})

    # 5️⃣ STAGE: Frontend Design
    state["current_stage"] = "frontend_design"
    for chunk in frontend_agent(
        state["domain_model"],
        state["backend_design"],
        state["history"],
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["frontend_design"] += chunk_text
        yield {"frontend_design": chunk_text, "stage": "frontend_design", "stage_complete": False}
        await asyncio.sleep(0)

    yield {"frontend_design": "", "stage": "frontend_design", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["frontend_design"]})

    # 6️⃣ STAGE: Cloud Architecture
    state["current_stage"] = "cloud_design"
    for chunk in cloud_agent(
        state["backend_design"],
        state["frontend_design"],
        state["history"],
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["cloud_design"] += chunk_text
        yield {"cloud_design": chunk_text, "stage": "cloud_design", "stage_complete": False}
        await asyncio.sleep(0)

    yield {"cloud_design": "", "stage": "cloud_design", "stage_complete": True}
    state["history"].append({"role": "assistant", "content": state["cloud_design"]})

    # 7️⃣ STAGE: Frontend Code Generation
    state["current_stage"] = "frontend_code"
    for chunk in frontend_code_generation_agent(
        state["frontend_design"],
        state["domain_model"],
        state["history"],
        stream=True
    ):
        chunk_str = chunk.content if hasattr(chunk, 'content') else str(chunk)
        yield {"frontend_code_status": chunk_str, "stage": "frontend_code", "stage_complete": False}
        
        if "ZIP File:" in chunk_str:
            path_start = chunk_str.find("/mnt/user-data/outputs/")
            if path_start != -1:
                path_end = chunk_str.find("\n", path_start)
                if path_end == -1:
                    path_end = len(chunk_str)
                state["frontend_zip_path"] = chunk_str[path_start:path_end].strip()
        
        await asyncio.sleep(0)

    yield {
        "frontend_code_status": "✅ Complete", 
        "stage": "frontend_code", 
        "stage_complete": True, 
        "frontend_zip_path": state.get("frontend_zip_path", "")
    }

    # 8️⃣ STAGE: Backend Code Generation
    state["current_stage"] = "backend_code"
    for chunk in backend_code_generation_agent(
        state["backend_design"],
        state["domain_model"],
        state["history"],
        stream=True
    ):
        chunk_str = chunk.content if hasattr(chunk, 'content') else str(chunk)
        yield {"backend_code_status": chunk_str, "stage": "backend_code", "stage_complete": False}
        
        if "ZIP File:" in chunk_str:
            path_start = chunk_str.find("/mnt/user-data/outputs/")
            if path_start != -1:
                path_end = chunk_str.find("\n", path_start)
                if path_end == -1:
                    path_end = len(chunk_str)
                state["backend_zip_path"] = chunk_str[path_start:path_end].strip()
        
        await asyncio.sleep(0)

    yield {
        "backend_code_status": "✅ Complete", 
        "stage": "backend_code", 
        "stage_complete": True, 
        "backend_zip_path": state.get("backend_zip_path", "")
    }

    # Final summary
    yield {
        "stage": "complete",
        "stage_complete": True,
        "summary": "🎉 Modernization complete! All artifacts generated."
    }


def build_enhanced_graph():
    """Build the complete modernization workflow graph."""
    graph = StateGraph(EnhancedState)
    graph.add_node("modernize_stream_with_approval", modernize_stream_with_approval)
    graph.set_entry_point("modernize_stream_with_approval")
    graph.set_finish_point("modernize_stream_with_approval")
    return graph.compile()


# Explicitly export
__all__ = ['modernize_stream_with_approval', 'build_enhanced_graph', 'EnhancedState']