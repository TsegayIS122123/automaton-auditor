"""Detective nodes that produce structured Evidence objects - pure facts, no opinions"""

import json
from typing import Dict, Any, List
from datetime import datetime

from ..state import AgentState, Evidence
from ..tools.repo_tools import RepoInvestigator
from ..tools.doc_tools import DocAnalyst
from ..rubric_loader import RubricLoader

def repo_investigator_node(state: AgentState) -> Dict[str, List[Evidence]]:
    """
    LangGraph node that collects evidence from GitHub repository.
    Returns structured Evidence objects - pure facts, no opinions.
    """
    evidences = []
    
    try:
        # Load rubric to know what to look for
        rubric = RubricLoader()
        repo_dimensions = rubric.get_dimensions_by_artifact("github_repo")
        
        # Use context manager for automatic cleanup
        with RepoInvestigator(state["repo_url"]) as investigator:
            
            # Analyze git history
            git_history = investigator.analyze_git_history()
            evidences.append(Evidence(
                goal="Git commit history shows progression (setup → tools → graph)",
                found=git_history.get("total_commits", 0) > 3,
                content=json.dumps({
                    "total_commits": git_history.get("total_commits", 0),
                    "has_progression": git_history.get("has_progression", False),
                    "recent_commits": git_history.get("commits", [])[:3]
                }, indent=2),
                location="git log",
                rationale=f"Found {git_history.get('total_commits', 0)} commits. Progression: {git_history.get('has_progression', False)}",
                confidence=0.9 if git_history.get("has_progression") else 0.5,
                collected_by="RepoInvestigator"
            ))
            
            # Analyze graph structure with AST
            graph_analysis = investigator.analyze_graph_structure()
            evidences.append(Evidence(
                goal="Graph has parallel fan-out architecture",
                found=graph_analysis.get("has_parallel", False),
                content=json.dumps(graph_analysis, indent=2),
                location="src/graph.py",
                rationale=f"Parallel execution: {graph_analysis.get('has_parallel', False)}. Fan-out: {graph_analysis.get('has_fan_out', False)}",
                confidence=0.95 if graph_analysis.get("has_parallel") else 0.3,
                collected_by="RepoInvestigator"
            ))
            
            # Check state models
            state_analysis = investigator.check_state_models()
            evidences.append(Evidence(
                goal="State uses Pydantic with reducers",
                found=state_analysis.get("has_reducers", False) and state_analysis.get("has_evidence", False),
                content=json.dumps(state_analysis, indent=2),
                location="src/state.py",
                rationale=f"Reducers: {state_analysis.get('has_reducers', False)}. Evidence class: {state_analysis.get('has_evidence', False)}",
                confidence=0.95 if state_analysis.get("has_reducers") else 0.3,
                collected_by="RepoInvestigator"
            ))
            
            # Check sandboxing
            sandbox_analysis = investigator.check_sandboxing()
            evidences.append(Evidence(
                goal="Tools use proper sandboxing (tempfile, no os.system)",
                found=sandbox_analysis.get("has_tempfile", False) and sandbox_analysis.get("no_os_system", True),
                content=json.dumps(sandbox_analysis, indent=2),
                location="src/tools/",
                rationale=f"Tempfile: {sandbox_analysis.get('has_tempfile', False)}. No os.system: {sandbox_analysis.get('no_os_system', True)}",
                confidence=0.9 if sandbox_analysis.get("has_tempfile") else 0.2,
                collected_by="RepoInvestigator"
            ))
            
    except Exception as e:
        # Graceful error handling - still return evidence
        evidences.append(Evidence(
            goal="Clone and analyze repository successfully",
            found=False,
            content=str(e),
            location=state["repo_url"],
            rationale=f"Error during investigation: {str(e)}",
            confidence=0.0,
            collected_by="RepoInvestigator"
        ))
    
    return {"evidences": {"repo": evidences}}

def doc_analyst_node(state: AgentState) -> Dict[str, List[Evidence]]:
    """
    LangGraph node that collects evidence from PDF report.
    Returns structured Evidence objects - pure facts, no opinions.
    """
    evidences = []
    
    try:
        analyst = DocAnalyst(state["pdf_path"])
        
        # Extract text and create chunks
        analyst.extract_text()
        analyst.chunk_text()
        
        # Check for deep concept explanations
        concepts = ["Dialectical Synthesis", "Fan-In", "Fan-Out", "Metacognition", "State Synchronization"]
        for concept in concepts:
            analysis = analyst.check_concept_depth(concept)
            evidences.append(Evidence(
                goal=f"PDF explains '{concept}' in depth (not just keyword dropping)",
                found=analysis["depth"] == "deep",
                content=json.dumps({
                    "depth": analysis["depth"],
                    "explanation_preview": analysis["explanations"][0] if analysis["explanations"] else None
                }, indent=2),
                location=f"PDF: {concept} section",
                rationale=f"Depth: {analysis['depth']}. {'Found explanation' if analysis['explanations'] else 'Keyword only'}",
                confidence=0.9 if analysis["depth"] == "deep" else 0.4 if analysis["depth"] == "moderate" else 0.1,
                collected_by="DocAnalyst"
            ))
        
        # Extract file paths for cross-reference
        file_paths = analyst.extract_file_paths()
        evidences.append(Evidence(
            goal="PDF mentions specific file paths that can be cross-referenced",
            found=len(file_paths) > 0,
            content=json.dumps(file_paths[:10], indent=2),  # First 10 paths
            location="PDF file paths",
            rationale=f"Found {len(file_paths)} file paths in PDF",
            confidence=0.8 if len(file_paths) > 0 else 0.1,
            collected_by="DocAnalyst"
        ))
        
        # Check for architecture diagram mentions
        diagram_mentions = analyst.query_concept("diagram")
        evidences.append(Evidence(
            goal="PDF includes architecture diagrams",
            found=len(diagram_mentions) > 0,
            content=json.dumps([m["text"][:100] for m in diagram_mentions[:2]], indent=2),
            location="PDF diagrams section",
            rationale=f"Found {len(diagram_mentions)} mentions of diagrams",
            confidence=0.7 if len(diagram_mentions) > 0 else 0.1,
            collected_by="DocAnalyst"
        ))
        
    except FileNotFoundError as e:
        evidences.append(Evidence(
            goal="Access PDF file",
            found=False,
            content=str(e),
            location=state["pdf_path"],
            rationale=f"PDF file not found: {str(e)}",
            confidence=0.0,
            collected_by="DocAnalyst"
        ))
    except Exception as e:
        evidences.append(Evidence(
            goal="Parse PDF successfully",
            found=False,
            content=str(e),
            location=state["pdf_path"],
            rationale=f"Error parsing PDF: {str(e)}",
            confidence=0.0,
            collected_by="DocAnalyst"
        ))
    
    return {"evidences": {"doc": evidences}}

def evidence_aggregator_node(state: AgentState) -> Dict:
    """
    Synchronization node that collects evidence from all detectives.
    This node enables fan-in pattern - waits for all parallel detectives to complete.
    """
    # Count evidence by source
    evidence_summary = {}
    for source, ev_list in state["evidences"].items():
        evidence_summary[source] = len(ev_list)
    
    total_evidence = sum(len(ev_list) for ev_list in state["evidences"].values())
    
    print(f"\n📊 Evidence Aggregator: Collected {total_evidence} evidence items")
    for source, count in evidence_summary.items():
        print(f"   - {source}: {count} items")
    
    # No state changes - just a synchronization point
    return {}