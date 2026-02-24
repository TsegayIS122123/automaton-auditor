"""Detective nodes for evidence collection"""

from langgraph.graph import StateGraph
from ..state import AgentState, Evidence
from ..tools.repo_tools import RepoInvestigator
from ..tools.doc_tools import DocAnalyst
import json
from datetime import datetime

def load_rubric() -> list:
    """Load rubric dimensions from JSON"""
    # In production, load from file
    return [
        {
            "id": "git_forensic_analysis",
            "name": "Git Forensic Analysis",
            "target_artifact": "github_repo",
            "forensic_instruction": "Analyze commit history for progression"
        },
        {
            "id": "state_management_rigor",
            "name": "State Management Rigor",
            "target_artifact": "github_repo",
            "forensic_instruction": "Check for Pydantic models with reducers"
        },
        {
            "id": "theoretical_depth",
            "name": "Theoretical Depth",
            "target_artifact": "pdf_report",
            "forensic_instruction": "Check for deep explanation of concepts"
        }
    ]

def repo_investigator_node(state: AgentState) -> dict:
    """Collect evidence from GitHub repository"""
    evidences = []
    
    try:
        with RepoInvestigator(state["repo_url"]) as investigator:
            
            # Analyze git history
            git_history = investigator.analyze_git_history()
            evidences.append(Evidence(
                goal="Git commit history shows progression",
                found=git_history.get("total_commits", 0) > 3,
                content=json.dumps(git_history, indent=2),
                location="git log",
                rationale=f"Found {git_history.get('total_commits', 0)} commits",
                confidence=0.9 if git_history.get("has_progression") else 0.5,
                collected_by="RepoInvestigator"
            ))
            
            # Analyze graph structure
            graph_analysis = investigator.analyze_graph_structure()
            evidences.append(Evidence(
                goal="Graph has parallel fan-out/fan-in",
                found=graph_analysis.get("has_parallel", False),
                content=json.dumps(graph_analysis, indent=2),
                location="src/graph.py",
                rationale=f"Parallel: {graph_analysis.get('has_parallel', False)}",
                confidence=0.95 if graph_analysis.get("has_parallel") else 0.3,
                collected_by="RepoInvestigator"
            ))
            
            # Check state models
            state_analysis = investigator.check_state_models()
            evidences.append(Evidence(
                goal="State uses Pydantic with reducers",
                found=state_analysis.get("has_reducers", False),
                content=json.dumps(state_analysis, indent=2),
                location="src/state.py",
                rationale=f"Reducers: {state_analysis.get('has_reducers', False)}",
                confidence=0.95 if state_analysis.get("has_reducers") else 0.3,
                collected_by="RepoInvestigator"
            ))
            
            # Check sandboxing
            sandbox_analysis = investigator.check_sandboxing()
            evidences.append(Evidence(
                goal="Tools use proper sandboxing",
                found=sandbox_analysis.get("has_tempfile", False),
                content=json.dumps(sandbox_analysis, indent=2),
                location="src/tools/",
                rationale=f"Tempfile: {sandbox_analysis.get('has_tempfile', False)}",
                confidence=0.9 if sandbox_analysis.get("has_tempfile") else 0.2,
                collected_by="RepoInvestigator"
            ))
            
    except Exception as e:
        evidences.append(Evidence(
            goal="Clone repository successfully",
            found=False,
            content=str(e),
            location=state["repo_url"],
            rationale=f"Error: {str(e)}",
            confidence=0.0,
            collected_by="RepoInvestigator"
        ))
    
    return {"evidences": {"repo": evidences}}

def doc_analyst_node(state: AgentState) -> dict:
    """Collect evidence from PDF report"""
    evidences = []
    
    try:
        analyst = DocAnalyst(state["pdf_path"])
        
        # Check for deep concept explanations
        concepts = ["Dialectical Synthesis", "Fan-In/Fan-Out", "Metacognition"]
        for concept in concepts:
            analysis = analyst.check_concept_depth(concept)
            evidences.append(Evidence(
                goal=f"PDF explains '{concept}' in depth",
                found=analysis["depth"] == "deep",
                content=json.dumps(analysis, indent=2),
                location=f"PDF: {concept}",
                rationale=f"Depth: {analysis['depth']}",
                confidence=0.9 if analysis["depth"] == "deep" else 0.3,
                collected_by="DocAnalyst"
            ))
        
        # Extract file paths for cross-reference
        file_paths = analyst.extract_file_paths()
        evidences.append(Evidence(
            goal="PDF mentions specific file paths",
            found=len(file_paths) > 0,
            content=json.dumps(file_paths, indent=2),
            location="PDF file paths",
            rationale=f"Found {len(file_paths)} file paths",
            confidence=0.8 if len(file_paths) > 0 else 0.1,
            collected_by="DocAnalyst"
        ))
        
    except Exception as e:
        evidences.append(Evidence(
            goal="Parse PDF successfully",
            found=False,
            content=str(e),
            location=state["pdf_path"],
            rationale=f"Error: {str(e)}",
            confidence=0.0,
            collected_by="DocAnalyst"
        ))
    
    return {"evidences": {"doc": evidences}}

def evidence_aggregator_node(state: AgentState) -> dict:
    """Synchronize and validate evidence from all detectives"""
    
    # Evidence is already merged via reducer, just validate
    all_evidence = []
    for source, ev_list in state["evidences"].items():
        all_evidence.extend(ev_list)
    
    # Log summary
    print(f"📊 Evidence Aggregator: Collected {len(all_evidence)} evidence items")
    
    # You could add validation logic here
    
    return {}  # No state change needed, just sync point