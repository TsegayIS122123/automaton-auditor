"""LangGraph state machine with parallel detective layer and error handling"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, Literal

from .state import AgentState
from .nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node
)
from .rubric_loader import RubricLoader

def should_retry_or_fail(state: AgentState) -> Literal["continue", "retry", "fail"]:
    """Conditional edge: Check if evidence collection succeeded"""
    
    # Count errors
    error_count = len(state.get("errors", []))
    
    if error_count > 3:
        return "fail"  # Too many errors, abort
    elif error_count > 0:
        return "retry"  # Some errors, retry once
    else:
        return "continue"  # No errors, proceed

def check_evidence_exists(state: AgentState) -> Literal["has_evidence", "missing_evidence"]:
    """Conditional edge: Check if any evidence was collected"""
    
    total_evidence = sum(len(ev_list) for ev_list in state["evidences"].values())
    
    if total_evidence == 0:
        return "missing_evidence"
    return "has_evidence"

def create_detective_graph():
    """
    Create graph with detective layer and conditional error handling.
    Features:
    - Parallel fan-out: START → [Repo, Doc]
    - Fan-in: [Repo, Doc] → EvidenceAggregator
    - Conditional edges for error handling and retry logic
    """
    
    # Load rubric dynamically
    rubric = RubricLoader()
    
    # Initialize graph with state schema
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)
    builder.add_node("error_handler", handle_errors)  # New error handling node
    builder.add_node("retry_node", retry_operation)    # New retry node
    
    # FAN-OUT: Both detectives start in parallel
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    
    # FAN-IN: Both feed into aggregator
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    
    # CONDITIONAL EDGE: Check errors after aggregation
    builder.add_conditional_edges(
        "evidence_aggregator",
        should_retry_or_fail,
        {
            "continue": "check_evidence",  # No errors, check evidence
            "retry": "retry_node",          # Some errors, retry
            "fail": "error_handler"         # Too many errors, fail
        }
    )
    
    # Add evidence check node
    builder.add_node("check_evidence", check_evidence_node)
    
    # CONDITIONAL EDGE: Check if evidence exists
    builder.add_conditional_edges(
        "check_evidence",
        check_evidence_exists,
        {
            "has_evidence": END,           # Success - we have evidence
            "missing_evidence": "error_handler"  # No evidence - error
        }
    )
    
    # Error handling paths
    builder.add_edge("retry_node", "repo_investigator")  # Retry detectives
    builder.add_edge("error_handler", END)                # End with error
    
    # Add memory for state persistence
    memory = MemorySaver()
    
    # Compile graph
    graph = builder.compile(checkpointer=memory)
    
    return graph

def handle_errors(state: AgentState) -> Dict:
    """Error handling node"""
    print(f"⚠️ Error Handler: {len(state.get('errors', []))} errors occurred")
    for error in state.get("errors", [])[:3]:
        print(f"  - {error}")
    return {"warnings": ["Graph terminated due to errors"]}

def retry_operation(state: AgentState) -> Dict:
    """Retry logic node"""
    print("🔄 Retrying failed operations...")
    # Clear errors for retry
    return {"errors": []}

def check_evidence_node(state: AgentState) -> Dict:
    """Check if evidence was collected"""
    total = sum(len(ev_list) for ev_list in state["evidences"].values())
    print(f"📊 Evidence Check: {total} items collected")
    return {}

def run_detective_phase(repo_url: str, pdf_path: str) -> Dict[str, Any]:
    """
    Helper function to run the detective phase against a target.
    Now includes error handling and conditional routing.
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
    
    try:
        # Run with a dummy thread ID
        result = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": f"audit-{hash(repo_url)}"}}
        )
        return result
    except Exception as e:
        print(f"❌ Graph execution error: {e}")
        return {**initial_state, "errors": [str(e)]}

# For testing
if __name__ == "__main__":
    print("🚀 Testing detective graph with error handling...")
    result = run_detective_phase(
        repo_url="https://github.com/langchain-ai/langgraph",
        pdf_path="reports/interim_report.pdf"
    )
    print(f"\n✅ Graph executed successfully!")
    print(f"📊 Collected {sum(len(e) for e in result['evidences'].values())} evidence items")
    print(f"⚠️ Errors: {len(result.get('errors', []))}")
    print(f"⚠️ Warnings: {len(result.get('warnings', []))}")