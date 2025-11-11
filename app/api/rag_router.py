# app/api/rag_router.py

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from app.preprocessing.preprocessing import load_rag_chain

router = APIRouter()
rag_chain = load_rag_chain()

class QueryRequest(BaseModel):
    question: str

#router.post("/rag/query")
@router.post("/query")
async def query_rag(request: QueryRequest):
    try:
        result = rag_chain.invoke({"question": request.question})
        answer_obj = result.get("answer")
        if isinstance(answer_obj, AIMessage):
            answer_text = answer_obj.content
        else:
            answer_text = str(answer_obj)

        # print("additional_kwargs: ",answer_obj.additional_kwargs)
        # print("response metadata: ",answer_obj.response_metadata)
        # sources = result.get("")
        return {"answer": str(answer_text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
