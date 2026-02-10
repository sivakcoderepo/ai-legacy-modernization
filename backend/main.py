from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel
from graph.orchestrator import build_graph, analyze_stream
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------
# CORS setup
# -----------------------
origins = ["http://localhost:5500", "http://127.0.0.1:5500", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Models
# -----------------------
class ChatRequest(BaseModel):
    message: str

# -----------------------
# Health check
# -----------------------
@app.get("/")
def root():
    return {"status": "Backend running"}

# -----------------------
# Streaming chat
# -----------------------
@app.post("/chat/stream")
async def chat_stream(req: Request):
    body = await req.json()
    vb_code = body.get("message", "")

    async def event_generator():
        state = {
            "vb_code": vb_code,
            "history": [],
            "business_logic": "",
            "domain_model": "",
            "backend_design": "",
            "frontend_design": "",
            "cloud_design": ""
        }

        # Call async generator from orchestrator
        async for chunk in analyze_stream(state):
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
