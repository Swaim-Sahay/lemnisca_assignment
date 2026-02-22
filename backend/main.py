import time
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4

import backend.config as config
from backend.rag import DocumentStore
from backend.router import classify_query, get_model_for_classification
from backend.llm import generate_answer
from backend.evaluator import evaluate_response

app = FastAPI()

# Initialize and load DocumentStore
try:
    store = DocumentStore()
    store.load(config.VECTOR_STORE_PATH)
except Exception as e:
    print(f"Warning: Could not load vector store on startup: {e}")
    store = None

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class Source(BaseModel):
    document: str
    page: int
    relevance_score: float

class Metadata(BaseModel):
    model_used: str
    classification: str
    tokens: Dict[str, int]
    latency_ms: int
    chunks_retrieved: int
    evaluator_flags: List[str]

class QueryResponse(BaseModel):
    answer: str
    metadata: Metadata
    sources: List[Source]
    conversation_id: str

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    if not store:
        raise HTTPException(status_code=500, detail="Vector store not loaded.")
        
    start_time = time.time()
    conv_id = req.conversation_id or str(uuid4())
    
    # 1. Routing
    classification = classify_query(req.question)
    model_name = get_model_for_classification(classification)
    
    # 2. RAG Retrieval
    chunks = store.retrieve(req.question, top_k=5)
    
    # 3. LLM Generation
    try:
        answer, tokens = generate_answer(req.question, model_name, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
        
    # 4. Evaluation
    flags = evaluate_response(answer, len(chunks))
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    sources = [
        Source(
            document=c["document"],
            page=c["page"],
            relevance_score=round(c.get("relevance_score", 0.0), 3)
        ) for c in chunks
    ]
    
    metadata = Metadata(
        model_used=model_name,
        classification=classification,
        tokens=tokens,
        latency_ms=latency_ms,
        chunks_retrieved=len(chunks),
        evaluator_flags=flags
    )
    
    # Log the routing decision per requirements
    log_entry = {
        "query": req.question,
        "classification": classification,
        "model_used": model_name,
        "tokens_input": tokens["input"],
        "tokens_output": tokens["output"],
        "latency_ms": latency_ms
    }
    print(json.dumps(log_entry))
    
    return QueryResponse(
        answer=answer,
        metadata=metadata,
        sources=sources,
        conversation_id=conv_id
    )
