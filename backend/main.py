# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from graph.orchestrator import run_graph  # use the helper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Allow CORS
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str



# Health check
@app.get("/")
def root():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    state = {
        "vb_code": req.message,
        "history": [],
        "business_logic": "",
        "domain_model": "",
        "backend_design": "",
        "frontend_design": "",
        "cloud_design": ""
    }
    try:
        result = run_graph(state)
        return result
    except Exception as e:
        return {"error": str(e)}
