"""
Session router - handles GET /session/{id} endpoint
"""

from fastapi import APIRouter, HTTPException, Path
from typing import List
from datetime import datetime

from app.models.student import SessionResponse, MessageModel

router = APIRouter(prefix="/api", tags=["session"])

# Reference to sessions from chat router
# In production, this would use a database
sessions = {}


def get_sessions_ref():
    """Get reference to sessions storage"""
    from app.routers.chat import sessions as chat_sessions
    return chat_sessions


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str = Path(..., description="Session ID")
) -> SessionResponse:
    """
    Get session details by ID.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        SessionResponse with session details
        
    Raises:
        HTTPException: If session not found
    """
    sessions_ref = get_sessions_ref()
    
    if session_id not in sessions_ref:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )
    
    session = sessions_ref[session_id]
    
    # Convert messages to MessageModel
    messages = [
        MessageModel(
            role=msg.get("role", "user"),
            content=msg.get("content", ""),
        )
        for msg in session.get("messages", [])
    ]
    
    return SessionResponse(
        session_id=session_id,
        topic=session["topic"],
        level=session["level"],
        language=session.get("language", "en"),
        character_name=session["character_name"],
        correct_answers=session["correct_answers"],
        total_attempts=session["total_attempts"],
        misconceptions=session["misconceptions"],
        messages=messages,
        created_at=session.get("created_at", datetime.utcnow()),
        last_activity=datetime.utcnow(),
    )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str = Path(..., description="Session ID")
) -> dict:
    """
    Delete a session by ID.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If session not found
    """
    sessions_ref = get_sessions_ref()
    
    if session_id not in sessions_ref:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )
    
    del sessions_ref[session_id]
    
    return {
        "message": f"Session {session_id} deleted successfully",
        "session_id": session_id,
    }


@router.get("/sessions")
async def list_sessions() -> dict:
    """
    List all active sessions.
    
    Returns:
        Dictionary of active sessions
    """
    sessions_ref = get_sessions_ref()
    
    return {
        "total_sessions": len(sessions_ref),
        "sessions": [
            {
                "session_id": sid,
                "topic": s["topic"],
                "level": s["level"],
                "language": s.get("language", "en"),
                "messages_count": len(s.get("messages", [])),
                "correct_answers": s["correct_answers"],
                "total_attempts": s["total_attempts"],
            }
            for sid, s in sessions_ref.items()
        ],
    }
