# app/main.py
# uv run uvicorn app.main:app --reload

import pysqlite3
import sys
sys.modules['sqlite3'] = pysqlite3  # override built-in sqlite3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI
from app.api.rag_router import router as rag_router
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware


root_path = os.getenv("FASTAPI_ROOT_PATH", "/prod")
app = FastAPI(title="AWS Bedrock RAG FastAPI on Lambda", root_path=root_path)
# Detect root path (Lambda uses '/prod' as stage by default)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint
# include your RAG endpoint
app.include_router(rag_router, prefix="/rag", tags=["RAG"])

# health check
@app.get("/")
def root():
    return {"message": "RAG API is running"}

# Lambda handler
handler = Mangum(app)