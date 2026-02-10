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
    vb_files: List[Dict]  # List of {filename, content}
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

async def modernize_stream(state: EnhancedState):
    """
    Complete modernization workflow with all features and real-time streaming.
    
    Features:
    - Business logic analysis
    - Use case generation
    - Domain model extraction
    - Domain model comparison (optional)
    - Backend design
    - Frontend design
    - Cloud architecture
    - Deployable frontend code (ZIP)
    - Deployable backend code (ZIP)
    
    Streaming: Each chunk is immediately yielded for real-time UI updates
    """
    state["history"].append({"role": "user", "content": f"Analyzing {len(state['vb_files'])} VB files"})

    # 1️⃣ Business Logic Analysis - STREAM EACH CHUNK
    combined_vb = "\n\n".join([f"=== {f['filename']} ===\n{f['content']}" for f in state["vb_files"]])
    
    for chunk in legacy_code_analyzer(combined_vb, state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["business_logic"] += chunk_text
        
        # Immediately yield for real-time UI update
        yield {"business_logic": chunk_text}
        await asyncio.sleep(0)  # Force immediate delivery

    state["history"].append({"role": "assistant", "content": state["business_logic"]})

    # 2️⃣ Use Case Generation - STREAM EACH CHUNK
    for chunk in use_case_generator_agent(
        "",  # Requirements doc (optional)
        state["business_logic"],
        state["history"],
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["use_case_document"] += chunk_text
        
        yield {"use_cases": chunk_text}
        await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": state["use_case_document"]})

    # 3️⃣ Domain Model - STREAM EACH CHUNK
    for chunk in domain_model_agent(state["business_logic"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["domain_model"] += chunk_text
        
        yield {"domain_model": chunk_text}
        await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": state["domain_model"]})

    # 4️⃣ Domain Mapping (if target domain provided) - STREAM EACH CHUNK
    if state.get("target_domain_model") and state["target_domain_model"].strip():
        for chunk in domain_mapping_agent(
            state["domain_model"], 
            state["target_domain_model"], 
            state["history"], 
            stream=True
        ):
            chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
            state["domain_mapping"] += chunk_text
            
            yield {"domain_mapping": chunk_text}
            await asyncio.sleep(0)

        state["history"].append({"role": "assistant", "content": state["domain_mapping"]})

    # 5️⃣ Backend Design - STREAM EACH CHUNK
    for chunk in backend_agent(state["domain_model"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["backend_design"] += chunk_text
        
        yield {"backend_design": chunk_text}
        await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": state["backend_design"]})

    # 6️⃣ Frontend Design - STREAM EACH CHUNK
    for chunk in frontend_agent(state["backend_design"], state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["frontend_design"] += chunk_text
        
        yield {"frontend_design": chunk_text}
        await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": state["frontend_design"]})

    # 7️⃣ Cloud Design - STREAM EACH CHUNK
    combined = state["backend_design"] + state["frontend_design"]
    for chunk in cloud_agent(combined, state["history"], stream=True):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        state["cloud_design"] += chunk_text
        
        yield {"cloud_design": chunk_text}
        await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": state["cloud_design"]})

    # 8️⃣ Frontend Code Generation (ZIP) - STREAM STATUS UPDATES
    yield {"status": "🎨 Generating deployable frontend code..."}
    await asyncio.sleep(0)
    
    for chunk in frontend_code_generation_agent(
        state["frontend_design"],
        state["domain_model"],
        state["history"],
        project_name="modernized-frontend",
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        
        yield {"frontend_code_status": chunk_text}
        await asyncio.sleep(0)
        
        # Extract zip path if present
        if "ZIP File:" in chunk_text:
            import re
            match = re.search(r'ZIP File: (.+\.zip)', chunk_text)
            if match:
                state["frontend_zip_path"] = match.group(1)
                # Also send the path separately for easy access
                yield {"frontend_zip_path": state["frontend_zip_path"]}
                await asyncio.sleep(0)

    # 9️⃣ Backend Code Generation (ZIP) - STREAM STATUS UPDATES
    yield {"status": "⚙️ Generating deployable backend code..."}
    await asyncio.sleep(0)
    
    for chunk in backend_code_generation_agent(
        state["backend_design"],
        state["domain_model"],
        state["history"],
        project_name="modernized-backend",
        stream=True
    ):
        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
        
        yield {"backend_code_status": chunk_text}
        await asyncio.sleep(0)
        
        # Extract zip path if present
        if "ZIP File:" in chunk_text:
            import re
            match = re.search(r'ZIP File: (.+\.zip)', chunk_text)
            if match:
                state["backend_zip_path"] = match.group(1)
                # Also send the path separately for easy access
                yield {"backend_zip_path": state["backend_zip_path"]}
                await asyncio.sleep(0)

    # 🔟 Final Summary
    summary = f"""
🎉 MODERNIZATION COMPLETE!

📦 Deliverables Generated:
- ✅ Business Logic Analysis
- ✅ Use Cases Document
- ✅ Domain Model
{f"- ✅ Domain Mapping Analysis" if state.get("domain_mapping") else ""}
- ✅ Backend Design (Spring Boot)
- ✅ Frontend Design (Angular)
- ✅ Cloud Architecture (AWS)
- ✅ Frontend Code: {state.get('frontend_zip_path', 'N/A')}
- ✅ Backend Code: {state.get('backend_zip_path', 'N/A')}

All artifacts ready for download and deployment!
"""
    yield {"final_summary": summary}
    await asyncio.sleep(0)

    state["history"].append({"role": "assistant", "content": summary})

def build_enhanced_graph():
    """Build the complete modernization workflow graph."""
    graph = StateGraph(EnhancedState)
    graph.add_node("modernize_stream", modernize_stream)
    graph.set_entry_point("modernize_stream")
    graph.set_finish_point("modernize_stream")
    return graph.compile()
