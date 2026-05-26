"""
LangGraph node functions for the learning workflow.

The lesson design is intentionally learner-centered:
- introduce the topic warmly
- ask what the learner already knows or wants help with
- teach one key idea at a time
- ask a checkpoint question
- respond to answers with feedback, correction, and the next step
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


def get_last_user_message(state: LearnerState) -> str:
    """Return the most recent learner message."""
    for message in reversed(state["messages"]):
        if message.get("role") == "user":
            return message.get("content", "")
    return ""


def get_recent_conversation(state: LearnerState, limit: int = 6) -> str:
    """Format recent conversation turns for prompt context."""
    return "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in state["messages"][-limit:]
    )


def join_sections(*sections: str) -> str:
    """Join non-empty response sections with learner-friendly spacing."""
    cleaned_sections = [section.strip() for section in sections if section and section.strip()]
    return "\n\n".join(cleaned_sections)


def learner_requested_help(message: str) -> bool:
    """Detect when the learner is asking for another explanation instead of answering."""
    normalized = message.strip().lower()
    help_markers = [
        "help",
        "hint",
        "explain",
        "i don't understand",
        "i do not understand",
        "can you explain",
        "what does this mean",
        "confused",
        "不懂",
        "不明白",
        "請解釋",
        "解释",
        "解釋",
        "可以再說",
        "再說明",
        "không hiểu",
        "giải thích",
        "gợi ý",
        "giúp",
    ]
    return any(marker in normalized for marker in help_markers)


def router_node(state: LearnerState) -> Literal["introduce", "plan", "assess", "celebrate", "teach"]:
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

    if state["mode"] == "goal_check":
        return "plan"

    # Mastery achieved - celebrate
    if state["correct_answers"] >= 3:
        return "celebrate"

    if state["mode"] == "quiz":
        if learner_requested_help(get_last_user_message(state)):
            return "teach"
        return "assess"

    # Default - teach/explain
    return "teach"


def introduce_node(state: LearnerState) -> dict[str, Any]:
    """
    Introduce the topic and invite the learner to share their starting point.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with assistant introduction and learner goal check
    """
    level_guidance = {
        "beginner": "very simple, everyday analogies",
        "intermediate": "relatable, practical examples",
        "advanced": "sophisticated concepts and connections",
    }
    language_instruction = get_language_instruction(state["language"])
    
    prompt = f"""You are {state['character_name']}, an enthusiastic AI tutor designing a structured lesson.

Topic: {state['topic']}
Learner level: {state['level']}

Create the opening of the lesson. Your response should:
1. Briefly introduce the topic in an inviting way.
2. Mention why this topic matters using {level_guidance.get(state['level'], 'clear examples')}.
3. Ask the learner what they already know, where they get stuck, or what they want to focus on first.

Keep it to 3 short sentences and make it feel like the first step of a lesson, not a full explanation.
{language_instruction}"""

    introduction = invoke_llm_with_debug(prompt, "introduce")
    
    assistant_message = {
        "role": "assistant",
        "content": introduction,
    }
    
    return {
        "messages": [assistant_message],
        "mode": "goal_check",
        "mood": "excited",
    }


def plan_node(state: LearnerState) -> dict[str, Any]:
    """
    Turn the learner's stated need into a short structured lesson opening.

    Returns:
        Updated state with learner goal, first explanation, and checkpoint question
    """
    last_user_message = get_last_user_message(state)
    language_instruction = get_language_instruction(state["language"])

    prompt = f"""You are {state['character_name']}, an AI tutor building a structured lesson.

Topic: {state['topic']}
Learner level: {state['level']}
Learner message: {last_user_message}

Write one response that does all of the following:
1. Acknowledge what the learner wants help with.
2. Tell them the lesson structure in one short sentence, such as "first we'll understand..., then we'll try a question."
3. Teach the first key idea simply.
4. End with exactly one checkpoint question.

Keep it concise, supportive, and interactive.
{language_instruction}"""

    lesson_opening = invoke_llm_with_debug(prompt, "plan")

    assistant_message = {
        "role": "assistant",
        "content": lesson_opening,
    }

    return {
        "messages": [assistant_message],
        "learner_goal": last_user_message,
        "mode": "quiz",
        "mood": "happy",
    }


def assess_node(state: LearnerState) -> dict[str, Any]:
    """
    Evaluate the learner's answer and continue the lesson interactively.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with feedback, next step, and checkpoint question
    """
    last_user_message = get_last_user_message(state)
    if not last_user_message:
        return {}

    conversation = get_recent_conversation(state)
    language_name = get_language_name(state["language"])
    
    prompt = f"""You are {state['character_name']}, running an interactive lesson.

Topic: {state['topic']}
Level: {state['level']}
Learner goal: {state['learner_goal'] or "not stated"}
Recent conversation:
{conversation}
Learner's latest response: {last_user_message}

Return valid JSON in this exact shape:
{{
  "verdict": "correct" | "partial" | "incorrect",
  "misconception": "string describing error or null",
  "feedback": "warm feedback about the learner's answer",
  "micro_explanation": "a short correction or next teaching step",
  "next_question": "exactly one follow-up checkpoint question"
}}

Rules:
- Keep "verdict" in English using only correct, partial, or incorrect.
- Write "feedback", "misconception", "micro_explanation", and "next_question" in {language_name}.
- If the learner is correct, briefly reinforce the idea and ask a slightly deeper question.
- If the learner is partial or incorrect, correct the misunderstanding gently and ask a simpler question that checks the key idea again.
- Keep the lesson moving one step at a time.
- Be kind and constructive."""

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
            "micro_explanation": "Let's look at the main idea one more time in a simpler way.",
            "next_question": "Can you try answering again in your own words?",
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
        "content": join_sections(
            evaluation.get("feedback", ""),
            evaluation.get("micro_explanation", ""),
            evaluation.get("next_question", ""),
        ),
    }
    
    # Build updates
    updates = {
        "messages": [assistant_message],
        "correct_answers": state["correct_answers"] + correct_increment,
        "total_attempts": state["total_attempts"] + 1,
        "mood": mood,
        "mode": "quiz",
    }
    
    # Add misconception if found
    if evaluation["misconception"]:
        misconceptions = state["misconceptions"] + [evaluation["misconception"]]
        updates["misconceptions"] = misconceptions
    
    return updates


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
3. Summarizes what they just learned
4. Suggests a related next topic to explore
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
    Provide a short explanation when the learner asks for help during the lesson.
    
    Args:
        state: Current LearnerState
        
    Returns:
        Updated state with explanation and a new checkpoint question
    """
    last_user_message = get_last_user_message(state)
    language_instruction = get_language_instruction(state["language"])

    prompt = f"""You are {state['character_name']}, continuing a structured lesson.

Topic: {state['topic']}
Level: {state['level']}
Learner goal: {state['learner_goal'] or "not stated"}
Learner's latest message: {last_user_message}

The learner is asking for more teaching or clarification.
Provide a response that:
1. Clarifies the idea in a simple, learner-friendly way
2. Uses one example appropriate for {state['level']} learners
3. Ends with exactly one checkpoint question
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
        "mood": "thinking",
    }
