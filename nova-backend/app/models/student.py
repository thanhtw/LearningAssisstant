"""
Pydantic models for student and chat interactions
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiosqlite
import os


class MessageModel(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="User message")
    topic: Optional[str] = Field("general", description="Learning topic")
    level: Optional[str] = Field("beginner", description="Difficulty level")
    language: Optional[str] = Field("en", description="Preferred response language")
    character_name: Optional[str] = Field("Nova", description="Tutor character name")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str
    message: str
    language: str = Field(description="Selected response language")
    mood: str = Field(description="Character mood")
    mode: str = Field(description="Interaction mode")
    correct_answers: int
    total_attempts: int
    misconceptions: List[str] = []


class SessionRequest(BaseModel):
    """Request to create or get session"""
    topic: str = Field(..., description="Learning topic")
    level: str = Field("beginner", description="Difficulty level")
    language: str = Field("en", description="Preferred response language")
    character_name: str = Field("Nova", description="Tutor character name")


class SessionResponse(BaseModel):
    """Session information response"""
    session_id: str
    topic: str
    level: str
    language: str
    character_name: str
    correct_answers: int
    total_attempts: int
    misconceptions: List[str]
    messages: List[MessageModel]
    created_at: datetime
    last_activity: datetime


class StudentProfile(BaseModel):
    """Student profile information"""
    student_id: str
    name: str
    level: str
    topics_studied: List[str] = []
    total_sessions: int = 0
    total_correct_answers: int = 0
    total_attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Database functions for progress tracking
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "progress.db")


async def init_database() -> None:
    """Initialize SQLite database with sessions and progress tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Create sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create progress table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                mastered BOOLEAN DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, topic_id)
            )
        """)
        
        await db.commit()


async def save_session_result(
    student_id: str,
    topic_id: str,
    correct: bool,
    attempts: int,
    session_id: str = None
) -> None:
    """
    Save or update a session result and student progress.
    
    Args:
        student_id: Student identifier
        topic_id: Topic being studied
        correct: Whether the last answer was correct
        attempts: Total attempts in this session
        session_id: Optional session ID to end
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # End the session if session_id provided
        if session_id:
            await db.execute(
                "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
        
        # Insert or update progress
        await db.execute("""
            INSERT INTO progress (student_id, topic_id, correct, attempts, last_seen)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, topic_id) DO UPDATE SET
                attempts = attempts + ?,
                correct = correct + ?,
                last_seen = CURRENT_TIMESTAMP
        """, (student_id, topic_id, 1 if correct else 0, attempts, attempts, 1 if correct else 0))
        
        await db.commit()


async def get_student_progress(student_id: str) -> Dict[str, Any]:
    """
    Get comprehensive progress for a student.
    
    Args:
        student_id: Student identifier
        
    Returns:
        Dictionary with progress statistics
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get overall stats
        cursor = await db.execute("""
            SELECT 
                COUNT(*) as total_topics,
                SUM(attempts) as total_attempts,
                SUM(correct) as total_correct,
                SUM(CASE WHEN mastered = 1 THEN 1 ELSE 0 END) as mastered_count
            FROM progress
            WHERE student_id = ?
        """, (student_id,))
        
        stats = await cursor.fetchone()
        
        # Get per-topic progress
        cursor = await db.execute("""
            SELECT topic_id, mastered, attempts, correct, last_seen
            FROM progress
            WHERE student_id = ?
            ORDER BY last_seen DESC
        """, (student_id,))
        
        topic_progress = []
        async for row in cursor:
            topic_progress.append({
                "topic_id": row[0],
                "mastered": bool(row[1]),
                "attempts": row[2],
                "correct": row[3],
                "last_seen": row[4],
                "accuracy": (row[3] / row[2] * 100) if row[2] > 0 else 0,
            })
        
        return {
            "student_id": student_id,
            "total_topics_studied": stats[0] or 0,
            "total_attempts": stats[1] or 0,
            "total_correct": stats[2] or 0,
            "mastered_count": stats[3] or 0,
            "overall_accuracy": (stats[2] / stats[1] * 100) if stats[1] and stats[1] > 0 else 0,
            "topic_progress": topic_progress,
        }


async def get_mastered_topics(student_id: str) -> List[str]:
    """
    Get list of topics mastered by a student.
    
    Args:
        student_id: Student identifier
        
    Returns:
        List of mastered topic IDs
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT topic_id FROM progress
            WHERE student_id = ? AND mastered = 1
            ORDER BY last_seen DESC
        """, (student_id,))
        
        topics = []
        async for row in cursor:
            topics.append(row[0])
        
        return topics


async def create_session(
    student_id: str,
    topic_id: str,
    session_id: str
) -> None:
    """
    Create a new learning session record.
    
    Args:
        student_id: Student identifier
        topic_id: Topic being studied
        session_id: Session identifier
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO sessions (id, student_id, topic_id, started_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (session_id, student_id, topic_id))
        
        await db.commit()


async def mark_topic_mastered(student_id: str, topic_id: str) -> None:
    """
    Mark a topic as mastered by a student.
    
    Args:
        student_id: Student identifier
        topic_id: Topic to mark as mastered
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE progress
            SET mastered = 1
            WHERE student_id = ? AND topic_id = ?
        """, (student_id, topic_id))
        
        await db.commit()
