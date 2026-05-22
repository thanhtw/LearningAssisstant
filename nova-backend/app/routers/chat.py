"""
Chat router - handles streaming POST /chat endpoint with SSE
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, AsyncGenerator
import uuid
from datetime import datetime
import json
import asyncio
import re

from app.models.student import ChatRequest
from app.graph.state import LearnerState
from app.graph.graph import graph

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
        
        # Config for graph with thread_id for persistence
        config = {"configurable": {"thread_id": session_id}}
        
        # Stream the graph execution
        accumulated_text = ""
        final_state = None
        
        async for event in graph.astream(learner_state, config=config):
            # event is a tuple of (node_name, output_dict)
            if isinstance(event, tuple):
                node_name, output = event
                if output and "messages" in output:
                    final_state = output
                    
                    # Extract new assistant message
                    messages = output.get("messages", [])
                    if messages:
                        last_msg = messages[-1]
                        if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
                            content = last_msg.get("content", "")
                            
                            # Parse [MOOD:xxx] tags
                            mood_match = re.search(r'\[MOOD:(\w+)\]', content)
                            if mood_match:
                                mood = mood_match.group(1)
                                # Send mood event
                                yield f"data: {json.dumps({'type': 'mood', 'mood': mood})}\n\n"
                                # Remove mood tag from content
                                content = re.sub(r'\[MOOD:\w+\]', '', content).strip()
                            
                            # Send token events for text chunks
                            if content and content != accumulated_text:
                                new_content = content[len(accumulated_text):]
                                if new_content:
                                    accumulated_text = content
                                    yield f"data: {json.dumps({'type': 'token', 'content': new_content})}\n\n"
        
        # Update session state from final output
        if final_state:
            session.update({
                "mood": final_state.get("mood", session["mood"]),
                "mode": final_state.get("mode", session["mode"]),
                "correct_answers": final_state.get("correct_answers", session["correct_answers"]),
                "total_attempts": final_state.get("total_attempts", session["total_attempts"]),
                "misconceptions": final_state.get("misconceptions", session["misconceptions"]),
                "level": final_state.get("level", session["level"]),
                "messages": final_state.get("messages", session["messages"]),
            })
        
        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'full_text': accumulated_text})}\n\n"
        
    except Exception as e:
        # Send error event
        error_msg = str(e) if isinstance(e, Exception) else "Unknown error"
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

