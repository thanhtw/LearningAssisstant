"""
LearnerState definition for LangGraph workflow
"""

from typing import List, Annotated, TypedDict
import operator


class LearnerState(TypedDict):
    """
    State dictionary for the learning graph workflow.
    
    Attributes:
        messages: Conversation history (accumulated over time)
        topic: Current learning topic
        level: Learner difficulty level ("beginner" | "intermediate" | "advanced")
        correct_answers: Count of correct answers in session
        total_attempts: Total number of quiz attempts
        misconceptions: List of identified misconceptions
        mode: Current interaction mode ("explain" | "quiz" | "hint" | "celebrate")
        mood: Character mood state
        character_name: Name of the AI tutor character
        language: Preferred response language code
        session_id: Unique session identifier
    """
    
    messages: Annotated[List[dict], operator.add]
    topic: str
    level: str
    correct_answers: int
    total_attempts: int
    misconceptions: List[str]
    mode: str
    mood: str
    character_name: str
    language: str
    session_id: str
