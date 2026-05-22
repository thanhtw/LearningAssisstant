"""
LangGraph node functions for the learning workflow
Implements interactive tutoring with Groq API and llama-3.3-70b-versatile
"""

from typing import Any, Literal
import json
import os
from langchain_groq import ChatGroq
from .state import LearnerState

# Initialize Groq LLM client
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=1024,
)


def router_node(state: LearnerState) -> Literal["introduce", "assess", "remediate", "celebrate", "teach"]:
    """
    Route to the appropriate node based on student state.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Next node name to execute
    """
    # First interaction - introduce topic
    if state["total_attempts"] == 0:
        return "introduce"
    
    # In quiz mode - assess answer
    if state["mode"] == "quiz":
        return "assess"
    
    # Low accuracy with multiple attempts - remediate
    accuracy = state["correct_answers"] / max(state["total_attempts"], 1)
    if accuracy < 0.4 and state["total_attempts"] > 2:
        return "remediate"
    
    # Mastery achieved - celebrate
    if state["correct_answers"] >= 3:
        return "celebrate"
    
    # Default - teach/explain
    return "teach"


def introduce_node(state: LearnerState) -> dict[str, Any]:
    """
    Introduce the topic with an engaging opening.
    
    Calls Claude to create an introduction with an analogy
    suited to the student's level, ending with a question.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with assistant introduction and quiz mode
    """
    level_guidance = {
        "beginner": "very simple, everyday analogies",
        "intermediate": "relatable, practical examples",
        "advanced": "sophisticated concepts and connections",
    }
    
    prompt = f"""You are {state['character_name']}, an enthusiastic AI tutor.

Introduce the topic: {state['topic']} for a {state['level']} learner.

Use {level_guidance.get(state['level'], 'clear examples')} and an analogy to make it engaging.
End with one compelling question to start the learning.

Keep it brief (2-3 sentences) and warm."""

    response = llm.invoke(prompt)
    introduction = response.content
    
    assistant_message = {
        "role": "assistant",
        "content": introduction,
    }
    
    return {
        "messages": [assistant_message],
        "mode": "quiz",
        "mood": "excited",
    }


def assess_node(state: LearnerState) -> dict[str, Any]:
    """
    Evaluate student's answer to the quiz question.
    
    Calls Claude to determine correctness, identify misconceptions,
    and provide encouraging feedback in character.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with feedback, correctness count, and mood
    """
    if not state["messages"]:
        return {}
    
    # Get the last user message (student's answer)
    last_user_message = None
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            last_user_message = msg.get("content", "")
            break
    
    if not last_user_message:
        return {}
    
    # Build context of conversation
    conversation = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in state["messages"][-4:]  # Last 4 messages for context
    ])
    
    prompt = f"""You are {state['character_name']}, evaluating a student's answer.

Topic: {state['topic']}
Level: {state['level']}
Student's answer: {last_user_message}

Evaluate in JSON format:
{{
  "verdict": "correct" | "partial" | "incorrect",
  "misconception": "string describing error or null",
  "feedback": "warm, encouraging feedback in character (1-2 sentences)"
}}

Be kind and constructive. Celebrate progress!"""

    response = llm.invoke(prompt)
    
    # Parse response
    try:
        # Extract JSON from response
        content = response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        evaluation = json.loads(content[json_start:json_end])
    except (json.JSONDecodeError, ValueError):
        # Fallback if JSON parsing fails
        evaluation = {
            "verdict": "partial",
            "misconception": None,
            "feedback": "Good attempt! Let's explore this more.",
        }
    
    # Update correctness
    correct_increment = 1 if evaluation["verdict"] == "correct" else 0
    
    # Determine mood based on verdict
    mood_map = {
        "correct": "happy",
        "partial": "thinking",
        "incorrect": "sad",
    }
    mood = mood_map.get(evaluation["verdict"], "neutral")
    
    # Build assistant response
    assistant_message = {
        "role": "assistant",
        "content": evaluation["feedback"],
    }
    
    # Build updates
    updates = {
        "messages": [assistant_message],
        "correct_answers": state["correct_answers"] + correct_increment,
        "total_attempts": state["total_attempts"] + 1,
        "mood": mood,
    }
    
    # Add misconception if found
    if evaluation["misconception"]:
        misconceptions = state["misconceptions"] + [evaluation["misconception"]]
        updates["misconceptions"] = misconceptions
    
    return updates


def remediate_node(state: LearnerState) -> dict[str, Any]:
    """
    Re-explain concepts using different analogies and approaches.
    
    Addresses identified misconceptions with encouraging tone.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with re-explanation and return to quiz mode
    """
    misconceptions_text = ", ".join(state["misconceptions"]) if state["misconceptions"] else "general confusion"
    
    prompt = f"""You are {state['character_name']}, re-teaching a concept.

Topic: {state['topic']}
Student misconceptions: {misconceptions_text}
Level: {state['level']}

Provide a fresh explanation using:
- A DIFFERENT analogy than before
- Simpler language if needed
- Clear steps or examples
- End with a supportive question to check understanding

Never be condescending. Always be encouraging!
Keep it brief (3-4 sentences)."""

    response = llm.invoke(prompt)
    remediation = response.content
    
    assistant_message = {
        "role": "assistant",
        "content": remediation,
    }
    
    return {
        "messages": [assistant_message],
        "mode": "quiz",
        "mood": "thinking",
    }


def celebrate_node(state: LearnerState) -> dict[str, Any]:
    """
    Celebrate student's mastery and suggest next topic.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with celebration and congratulations
    """
    accuracy = state["correct_answers"] / max(state["total_attempts"], 1) * 100
    
    prompt = f"""You are {state['character_name']}, celebrating a student's success!

Topic mastered: {state['topic']}
Level: {state['level']}
Accuracy: {accuracy:.0f}%

Write an enthusiastic, brief celebration (2-3 sentences) that:
1. Praises their achievement genuinely
2. Acknowledges their effort
3. Suggests a related next topic to explore

Be warm and encouraging!"""

    response = llm.invoke(prompt)
    celebration = response.content
    
    assistant_message = {
        "role": "assistant",
        "content": celebration,
    }
    
    return {
        "messages": [assistant_message],
        "mood": "excited",
    }


def teach_node(state: LearnerState) -> dict[str, Any]:
    """
    Provide general teaching and explanation.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with explanation
    """
    prompt = f"""You are {state['character_name']}, explaining a concept.

Topic: {state['topic']}
Level: {state['level']}

Provide a clear, engaging explanation that:
1. Uses examples appropriate for {state['level']} learners
2. Is concise (2-3 sentences)
3. Ends with a question to deepen understanding

Make it interactive and warm!"""

    response = llm.invoke(prompt)
    explanation = response.content
    
    assistant_message = {
        "role": "assistant",
        "content": explanation,
    }
    
    return {
        "messages": [assistant_message],
        "mode": "quiz",
    }
