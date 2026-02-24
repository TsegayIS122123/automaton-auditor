"""LangGraph state machine for Automaton Auditor"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint import MemorySaver
from .state import AgentState
from .nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node
)

def create_detective_graph():
    """Create partial graph with detective layer only"""
    
    # Initialize graph with state schema
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)
    
    # FAN-OUT: Both detectives start in parallel
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    
    # FAN-IN: Both feed into aggregator
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    
    # End after aggregation
    builder.add_edge("evidence_aggregator", END)
    
    # Add memory for state persistence
    memory = MemorySaver()
    
    # Compile graph
    graph = builder.compile(checkpointer=memory)
    
    return graph

# For testing
if __name__ == "__main__":
    # Create graph
    graph = create_detective_graph()
    
    # Test with dummy data
    initial_state = {
        "repo_url": "https://github.com/test/repo",
        "pdf_path": "report.pdf",
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": None,
        "errors": [],
        "warnings": []
    }
    
    print("🚀 Detective graph created successfully!")
    print(graph.get_graph().draw_ascii())