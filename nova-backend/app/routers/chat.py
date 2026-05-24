"""
Chat router - handles streaming POST /chat endpoint with SSE
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, AsyncGenerator
from datetime import datetime
import json
import re

from app.models.student import ChatRequest
from app.graph.state import LearnerState
from app.graph.graph import graph
from app.debug import debug_log

router = APIRouter(tags=["chat"])

# In-memory session storage (replace with database in production)
sessions: Dict[str, dict] = {}


async def stream_chat(session_id: str, message: str, topic: str, level: str, character_name: str) -> AsyncGenerator[str, None]:
    """
    Generator function for streaming chat responses with SSE.
    Parses [MOOD:xxx] tags from Claude responses and sends SSE events.
    
    Args:
        session_id: Unique session identifier
        message: User's input message
        topic: Topic being learned
        level: Learning level (beginner, intermediate, advanced)
        character_name: Character name for the session
        
    Yields:
        SSE formatted event strings
    """
    try:
        debug_log(
            "\n===== CHAT REQUEST =====\n"
            f"session_id={session_id}\n"
            f"topic={topic}\n"
            f"level={level}\n"
            f"character_name={character_name}\n"
            f"message={message}\n"
        )

        # Open the SSE stream immediately so the client can tell the backend was reached.
        yield f"data: {json.dumps({'type': 'status', 'message': 'started'})}\n\n"

        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "topic": topic,
                "level": level,
                "correct_answers": 0,
                "total_attempts": 0,
                "misconceptions": [],
                "mode": "explain",
                "mood": "happy",
                "character_name": character_name,
                "session_id": session_id,
                "created_at": datetime.utcnow(),
            }
        
        session = sessions[session_id]
        
        # Add user message
        user_message = {
            "role": "user",
            "content": message,
        }
        session["messages"].append(user_message)
        
        # Create LearnerState for graph execution
        learner_state: LearnerState = {
            "messages": session["messages"],
            "topic": session["topic"],
            "level": session["level"],
            "correct_answers": session["correct_answers"],
            "total_attempts": session["total_attempts"],
            "misconceptions": session["misconceptions"],
            "mode": session["mode"],
            "mood": session["mood"],
            "character_name": session["character_name"],
            "session_id": session_id,
        }

        final_state = await graph.ainvoke(learner_state)
        final_messages = final_state.get("messages", session["messages"])
        assistant_text = ""

        for msg in reversed(final_messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                assistant_text = msg.get("content", "")
                break

        mood = final_state.get("mood", session["mood"])
        mood_match = re.search(r"\[MOOD:(\w+)\]", assistant_text)
        if mood_match:
            mood = mood_match.group(1)
            assistant_text = re.sub(r"\[MOOD:\w+\]", "", assistant_text).strip()

        session.update({
            "mood": mood,
            "mode": final_state.get("mode", session["mode"]),
            "correct_answers": final_state.get("correct_answers", session["correct_answers"]),
            "total_attempts": final_state.get("total_attempts", session["total_attempts"]),
            "misconceptions": final_state.get("misconceptions", session["misconceptions"]),
            "level": final_state.get("level", session["level"]),
            "messages": final_messages,
        })

        debug_log(
            "===== CHAT RESPONSE =====\n"
            f"mood={mood}\n"
            f"mode={session['mode']}\n"
            f"assistant={assistant_text}\n"
        )

        yield f"data: {json.dumps({'type': 'mood', 'mood': mood})}\n\n"
        yield f"data: {json.dumps({'type': 'token', 'content': assistant_text})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'full_text': assistant_text})}\n\n"
        
    except Exception as e:
        # Send error event
        error_msg = str(e) if isinstance(e, Exception) else "Unknown error"
        debug_log(f"===== CHAT ERROR =====\n{error_msg}\n")
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Streaming chat endpoint - process user message and stream tutor response with SSE.
    
    Args:
        request: ChatRequest with session_id, message, topic, level, character_name
        
    Returns:
        StreamingResponse with SSE events containing tokens, mood updates, and completion
    """
    debug_log(
        "\n===== CHAT ENDPOINT HIT =====\n"
        f"session_id={request.session_id}\n"
        f"topic={request.topic}\n"
        f"level={request.level}\n"
    )
    return StreamingResponse(
        stream_chat(
            session_id=request.session_id,
            message=request.message,
            topic=request.topic,
            level=request.level,
            character_name=request.character_name,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> Dict:
    """
    Get the current session state.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session details including topic, level, scores, and mood
        
    Raises:
        HTTPException: If session not found
    """
    if session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "topic": session["topic"],
        "level": session["level"],
        "character_name": session["character_name"],
        "correct_answers": session["correct_answers"],
        "total_attempts": session["total_attempts"],
        "misconceptions": session["misconceptions"],
        "mood": session["mood"],
        "mode": session["mode"],
        "message_count": len(session["messages"]),
        "created_at": session["created_at"].isoformat() if isinstance(session["created_at"], datetime) else session["created_at"],
    }
