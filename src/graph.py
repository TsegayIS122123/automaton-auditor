"""Complete StateGraph with parallel detectives, judges, and synthesis"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, Literal

from .state import AgentState
from .nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node
)
from .nodes.vision_inspector import vision_inspector_node
from .nodes.judges import prosecutor_node, defense_node, tech_lead_node
from .nodes.justice import chief_justice_node
from .rubric_loader import RubricLoader

def route_after_detectives(state: AgentState) -> Literal["proceed_to_judges", "error"]:
    """Route after evidence collection - proceed if evidence exists"""
    total_evidence = sum(len(ev_list) for ev_list in state["evidences"].values())
    error_count = len(state.get("errors", []))
    
    if error_count > 0 or total_evidence == 0:
        return "error"
    return "proceed_to_judges"

def route_after_judges(state: AgentState) -> Literal["proceed_to_justice", "error"]:
    """Route after judge deliberation - proceed if opinions exist"""
    if len(state.get("opinions", [])) == 0:
        return "error"
    return "proceed_to_justice"

def handle_errors(state: AgentState) -> Dict:
    """Error handling node"""
    print(f"⚠️ Error Handler: {len(state.get('errors', []))} errors occurred")
    for error in state.get("errors", [])[:3]:
        print(f"  - {error}")
    return {"warnings": ["Graph terminated due to errors"]}

def create_full_graph():
    """
    Create complete graph with all layers:
    - Detectives (parallel) → Aggregator
    - Judges (parallel) → Chief Justice
    - Conditional edges for error handling
    """
    # Load rubric
    rubric = RubricLoader()

    # Initialize graph
    builder = StateGraph(AgentState)

    # --- Add all nodes ---
    # Detectives
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("vision_inspector", vision_inspector_node)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)
    
    # Judges
    builder.add_node("prosecutor", prosecutor_node)
    builder.add_node("defense", defense_node)
    builder.add_node("tech_lead", tech_lead_node)
    
    # Chief Justice
    builder.add_node("chief_justice", chief_justice_node)
    
    # Error handling
    builder.add_node("error_handler", handle_errors)

    # --- Detective Layer: FAN-OUT ---
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    builder.add_edge(START, "vision_inspector")

    # --- Detective Layer: FAN-IN ---
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")

    # --- Conditional after detectives ---
    builder.add_conditional_edges(
        "evidence_aggregator",
        route_after_detectives,
        {
            "proceed_to_judges": "judges_entry",
            "error": "error_handler"
        }
    )

    # --- Judges entry point (fan-out) ---
    builder.add_node("judges_entry", lambda x: x)  # Pass-through node
    builder.add_edge("judges_entry", "prosecutor")
    builder.add_edge("judges_entry", "defense")
    builder.add_edge("judges_entry", "tech_lead")

    # --- Judges FAN-IN to Chief Justice ---
    builder.add_edge("prosecutor", "chief_justice")
    builder.add_edge("defense", "chief_justice")
    builder.add_edge("tech_lead", "chief_justice")

    # --- Final synthesis ---
    builder.add_edge("chief_justice", END)
    builder.add_edge("error_handler", END)

    # Compile with checkpointing
    graph = builder.compile(checkpointer=MemorySaver())
    
    return graph

def run_full_audit(repo_url: str, pdf_path: str) -> Dict[str, Any]:
    """
    Run complete audit with all layers.
    Returns final state with AuditReport.
    """
    rubric = RubricLoader()
    
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

    graph = create_full_graph()
    
    try:
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
    print("🚀 Testing full audit graph...")
    result = run_full_audit(
        repo_url="https://github.com/langchain-ai/langgraph",
        pdf_path="reports/interim_report.pdf"
    )
    print(f"\n✅ Graph executed successfully!")
    print(f"📊 Evidence collected: {sum(len(e) for e in result['evidences'].values())}")
    print(f"⚖️ Opinions generated: {len(result.get('opinions', []))}")
    print(f"📄 Final report: {'Generated' if result.get('final_report') else 'Not generated'}")