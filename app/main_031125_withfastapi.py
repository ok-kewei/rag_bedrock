# app/main.py
# uv run uvicorn app.main:app --reload

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI, HTTPException
from app.api.rag_router import router as rag_router

app = FastAPI(title="Bedrock RAG FastAPI")

# API Endpoint
# include your RAG endpoint
app.include_router(rag_router, prefix="/rag", tags=["RAG"])
# app.include_router(rag_router)

# health check
@app.get("/")
def root():
    return {"message": "RAG API is running"}

