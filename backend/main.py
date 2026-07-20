from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.chat_service import chat


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://qoshi.framer.website",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str


@app.get("/")
def home():
    return {
        "message": "Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def ask(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        result = chat(
            question=question,
            session_id=req.session_id,
        )

        return ChatResponse(
            session_id=result["session_id"],
            answer=result["answer"],
        )

    except Exception as error:
        print("[CHAT ENDPOINT ERROR]", error)

        raise HTTPException(
            status_code=500,
            detail="The AI service is currently unavailable.",
        )