"""LangGraph state machine with parallel detective layer"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any

from .state import AgentState
from .nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node
)
from .rubric_loader import RubricLoader

def create_detective_graph():
    """
    Create partial graph with detective layer only.
    Features:
    - Parallel fan-out: START → [Repo, Doc]
    - Fan-in: [Repo, Doc] → EvidenceAggregator
    - State reducers prevent data overwrites
    """
    
    # Load rubric dynamically (The Constitution)
    rubric = RubricLoader()
    
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

def run_detective_phase(repo_url: str, pdf_path: str) -> Dict[str, Any]:
    """
    Helper function to run the detective phase against a target.
    This is what users will call to test the graph.
    """
    # Load rubric
    rubric = RubricLoader()
    
    # Create initial state
    initial_state = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_dimensions": rubric.get_dimensions(),
        "evidences": {},
        "opinions": [],
        "final_report": None,
        "errors": [],
        "warnings": []
    }
    
    # Create and run graph
    graph = create_detective_graph()
    
    # Run with a dummy thread ID
    result = graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "interim-test-001"}}
    )
    
    return result

# For testing
if __name__ == "__main__":
    print("🚀 Testing detective graph...")
    
    # Test with dummy values (replace with real paths for actual testing)
    result = run_detective_phase(
        repo_url="https://github.com/test/repo",
        pdf_path="reports/interim_report.pdf"
    )
    
    # Print summary
    total_evidence = sum(len(ev_list) for ev_list in result["evidences"].values())
    print(f"\n✅ Graph executed successfully!")
    print(f"📊 Collected {total_evidence} evidence items")
    print(f"   Repo evidence: {len(result['evidences'].get('repo', []))}")
    print(f"   Doc evidence: {len(result['evidences'].get('doc', []))}")