"""
LangGraph node functions for the learning workflow
Implements interactive tutoring with Groq API and llama-3.3-70b-versatile
"""

from typing import Any, Literal
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from .state import LearnerState
from app.debug import debug_log

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

LANGUAGE_NAMES = {
    "en": "English",
    "zh-TW": "Traditional Chinese",
    "vi": "Vietnamese",
}


def get_llm() -> ChatGroq:
    """
    Build the Groq client lazily so missing configuration surfaces at request time.
    """
    return ChatGroq(
        model=os.getenv("MODEL", "llama-3.3-70b-versatile"),
        temperature=0.7,
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        timeout=float(os.getenv("LLM_TIMEOUT", "20")),
        max_retries=1,
    )


def invoke_llm_with_debug(prompt: str, node_name: str) -> str:
    """
    Invoke the LLM and print the prompt/response for debugging.
    """
    debug_log(f"\n===== LLM PROMPT ({node_name}) =====\n{prompt}\n")
    try:
        response = get_llm().invoke(prompt)
        content = response.content if isinstance(response.content, str) else str(response.content)
        debug_log(f"===== LLM RESPONSE ({node_name}) =====\n{content}\n")
        return content
    except Exception as exc:
        debug_log(f"===== LLM ERROR ({node_name}) =====\n{exc}\n")
        raise


def get_language_name(language: str) -> str:
    """Map frontend language codes to tutor-friendly language names."""
    return LANGUAGE_NAMES.get(language, "English")


def get_language_instruction(language: str) -> str:
    """Keep model responses aligned with the selected UI language."""
    language_name = get_language_name(language)
    return (
        f"Respond entirely in {language_name}. "
        "If you include code, keep the code in normal programming syntax and explain it in the selected language."
    )


def router_node(state: LearnerState) -> Literal["introduce", "assess", "remediate", "celebrate", "teach"]:
    """
    Route to the appropriate node based on student state.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Next node name to execute
    """
    # First interaction - introduce topic before the assistant has replied once.
    if not any(message.get("role") == "assistant" for message in state["messages"]):
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
    language_instruction = get_language_instruction(state["language"])
    
    prompt = f"""You are {state['character_name']}, an enthusiastic AI tutor.

Introduce the topic: {state['topic']} for a {state['level']} learner.

Use {level_guidance.get(state['level'], 'clear examples')} and an analogy to make it engaging.
End with one compelling question to start the learning.
{language_instruction}

Keep it brief (2-3 sentences) and warm."""

    introduction = invoke_llm_with_debug(prompt, "introduce")
    
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
    language_name = get_language_name(state["language"])
    
    prompt = f"""You are {state['character_name']}, evaluating a student's answer.

Topic: {state['topic']}
Level: {state['level']}
Recent conversation:
{conversation}
Student's answer: {last_user_message}

Return valid JSON in this exact shape:
{{
  "verdict": "correct" | "partial" | "incorrect",
  "misconception": "string describing error or null",
  "feedback": "warm, encouraging feedback in character (1-2 sentences)"
}}

Rules:
- Keep "verdict" in English using only correct, partial, or incorrect.
- Write "feedback" and "misconception" in {language_name}.
- Be kind and constructive. Celebrate progress!"""

    content = invoke_llm_with_debug(prompt, "assess")

    # Parse response
    try:
        # Extract JSON from response
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
    language_instruction = get_language_instruction(state["language"])
    
    prompt = f"""You are {state['character_name']}, re-teaching a concept.

Topic: {state['topic']}
Student misconceptions: {misconceptions_text}
Level: {state['level']}

Provide a fresh explanation using:
- A DIFFERENT analogy than before
- Simpler language if needed
- Clear steps or examples
- End with a supportive question to check understanding
{language_instruction}

Never be condescending. Always be encouraging!
Keep it brief (3-4 sentences)."""

    remediation = invoke_llm_with_debug(prompt, "remediate")
    
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
    language_instruction = get_language_instruction(state["language"])
    
    prompt = f"""You are {state['character_name']}, celebrating a student's success!

Topic mastered: {state['topic']}
Level: {state['level']}
Accuracy: {accuracy:.0f}%

Write an enthusiastic, brief celebration (2-3 sentences) that:
1. Praises their achievement genuinely
2. Acknowledges their effort
3. Suggests a related next topic to explore
{language_instruction}

Be warm and encouraging!"""

    celebration = invoke_llm_with_debug(prompt, "celebrate")
    
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
    language_instruction = get_language_instruction(state["language"])

    prompt = f"""You are {state['character_name']}, explaining a concept.

Topic: {state['topic']}
Level: {state['level']}

Provide a clear, engaging explanation that:
1. Uses examples appropriate for {state['level']} learners
2. Is concise (2-3 sentences)
3. Ends with a question to deepen understanding
{language_instruction}

Make it interactive and warm!"""

    explanation = invoke_llm_with_debug(prompt, "teach")
    
    assistant_message = {
        "role": "assistant",
        "content": explanation,
    }
    
    return {
        "messages": [assistant_message],
        "mode": "quiz",
    }
