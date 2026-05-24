"""
LangGraph StateGraph compilation and workflow definition
Orchestrates adaptive tutoring workflow with conditional routing
"""

from langgraph.graph import StateGraph, START, END
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
        Compiled StateGraph
    """
    graph = StateGraph(LearnerState)
    
    # Add all nodes
    graph.add_node("introduce", introduce_node)
    graph.add_node("assess", assess_node)
    graph.add_node("remediate", remediate_node)
    graph.add_node("celebrate", celebrate_node)
    graph.add_node("teach", teach_node)
    
    # Route each request to exactly one node, then stop.
    graph.add_conditional_edges(
        START,
        router_node,
        {
            "introduce": "introduce",
            "assess": "assess",
            "remediate": "remediate",
            "celebrate": "celebrate",
            "teach": "teach",
        }
    )
    
    graph.add_edge("introduce", END)
    graph.add_edge("assess", END)
    graph.add_edge("remediate", END)
    graph.add_edge("celebrate", END)
    graph.add_edge("teach", END)
    
    compiled_graph = graph.compile()
    
    return compiled_graph


# Create a singleton instance for session management
graph = create_learning_graph()


def invoke_learning_graph(initial_state: LearnerState, config: dict | None = None) -> dict:
    """
    Execute the learning graph with given initial state.
    
    Args:
        initial_state: Initial LearnerState for the workflow
        config: Optional graph config
        
    Returns:
        Final state after graph execution
    """
    if config is None:
        config = {"configurable": {"thread_id": initial_state.get("session_id", "default")}}
    
    output = graph.invoke(initial_state, config=config)
    return output
