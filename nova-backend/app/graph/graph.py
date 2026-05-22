"""
LangGraph StateGraph compilation and workflow definition
Orchestrates adaptive tutoring workflow with conditional routing
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import LearnerState
from .nodes import (
    router_node,
    introduce_node,
    assess_node,
    remediate_node,
    celebrate_node,
    teach_node,
)


def create_learning_graph():
    """
    Create and compile the learning workflow StateGraph.
    
    Workflow:
    - router_node: Conditional entry that routes to appropriate node
    - introduce_node: Greets student and explains topic
    - assess_node: Evaluates student answer and provides feedback
    - remediate_node: Addresses misconceptions with different explanation
    - celebrate_node: Celebrates mastery and progress
    - teach_node: Provides general explanation of concept
    
    Returns:
        Compiled StateGraph with MemorySaver checkpointer
    """
    graph = StateGraph(LearnerState)
    
    # Add all nodes
    graph.add_node("router", router_node)
    graph.add_node("introduce", introduce_node)
    graph.add_node("assess", assess_node)
    graph.add_node("remediate", remediate_node)
    graph.add_node("celebrate", celebrate_node)
    graph.add_node("teach", teach_node)
    
    # Set conditional entry point from START to router
    graph.add_conditional_edges(
        START,
        router_node,
        {
            "introduce": "introduce",
            "assess": "assess",
            "remediate": "remediate",
            "celebrate": "celebrate",
            "teach": "teach",
            "router": "router",
        }
    )
    
    # Add edges from action nodes
    # introduce → teach (after greeting)
    graph.add_edge("introduce", "teach")
    
    # assess has multiple paths - need router or conditional logic
    # For now, use simple edge flow
    graph.add_edge("assess", "teach")
    
    # remediate → assess (try again)
    graph.add_edge("remediate", "assess")
    
    # teach → router (continue workflow)
    graph.add_edge("teach", "router")
    
    # celebrate → router (continue or end)
    graph.add_edge("celebrate", "router")
    
    # Add conditional edges from router back to nodes
    graph.add_conditional_edges(
        "router",
        router_node,
        {
            "introduce": "introduce",
            "assess": "assess",
            "remediate": "remediate",
            "celebrate": "celebrate",
            "teach": "teach",
            END: END,
        }
    )
    
    # Add checkpointer for state persistence
    checkpointer = MemorySaver()
    
    # Compile the graph with checkpointer
    compiled_graph = graph.compile(checkpointer=checkpointer)
    
    return compiled_graph


# Create a singleton instance for session management
graph = create_learning_graph()


def invoke_learning_graph(initial_state: LearnerState, config: dict = None) -> dict:
    """
    Execute the learning graph with given initial state.
    
    Args:
        initial_state: Initial LearnerState for the workflow
        config: Optional config dict with thread_id for persistence
        
    Returns:
        Final state after graph execution
    """
    if config is None:
        config = {"configurable": {"thread_id": initial_state.get("session_id", "default")}}
    
    output = graph.invoke(initial_state, config=config)
    return output
