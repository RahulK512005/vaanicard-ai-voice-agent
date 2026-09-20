from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.conversation import ConversationState
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/api/conversation", tags=["Conversation"])

@router.post("", response_model=ConversationState)
async def create_or_get_conversation(session_id: Optional[str] = None):
    """Initialize or fetch conversation state for a session."""
    return conversation_service.get_or_create_session(session_id)

@router.get("/{session_id}", response_model=ConversationState)
async def get_conversation(session_id: str):
    """Retrieve full conversation state including history, entities, and active filters."""
    state = conversation_service.get_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return state

@router.delete("/{session_id}")
async def reset_conversation(session_id: str):
    """Reset / clear conversation history for a session."""
    conversation_service.reset_session(session_id)
    return {"message": f"Session '{session_id}' reset successfully"}
