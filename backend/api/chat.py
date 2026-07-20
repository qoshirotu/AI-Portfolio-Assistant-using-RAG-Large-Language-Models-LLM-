from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.chat_service import chat


router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000
    )

    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat_endpoint(
    payload: ChatRequest
):
    try:
        question = payload.question.strip()

        if not question:
            raise HTTPException(
                status_code=422,
                detail="Question cannot be empty."
            )

        result = chat(
            question=question,
            session_id=payload.session_id
        )

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Chat service returned no result."
            )

        session_id = result.get("session_id")
        answer = result.get("answer")

        if not session_id:
            raise HTTPException(
                status_code=500,
                detail="Chat service did not return a session_id."
            )

        if not answer:
            raise HTTPException(
                status_code=500,
                detail="Chat service did not return an answer."
            )

        return ChatResponse(
            session_id=session_id,
            answer=answer
        )

    except HTTPException:
        raise

    except Exception as error:
        print("[CHAT ENDPOINT ERROR]")
        print(error)

        raise HTTPException(
            status_code=500,
            detail="The AI service is currently unavailable."
        )