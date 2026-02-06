from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel
from graph.orchestrator import build_graph
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------
# CORS setup
# -----------------------
origins = ["http://localhost:5500", "*"]
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
# Streaming chat (new)
# -----------------------
graph = build_graph()

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
        async for chunk in graph.nodes["analyze_stream"](state):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
