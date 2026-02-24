# src/state.py
"""
State management for Automaton Auditor.
Pydantic models with reducers for parallel safety.
"""

from typing import Annotated, List, Dict, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator
from datetime import datetime


# ===== DETECTIVE LAYER OUTPUT =====

class Evidence(BaseModel):
    """Forensic evidence collected by detectives"""
    goal: str = Field(description="What we were looking for (rubric criterion)")
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None, description="Relevant content snippet")
    location: str = Field(description="File path, commit hash, or page number")
    rationale: str = Field(description="Why you're confident in this evidence")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    collected_by: str = Field(description="Which detective collected this")
    timestamp: datetime = Field(default_factory=datetime.now)


# ===== JUDICIAL LAYER OUTPUT =====

class JudicialOpinion(BaseModel):
    """Opinion from a single judge persona"""
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str
    score: int = Field(ge=1, le=5, description="Score 1-5 per rubric")
    argument: str = Field(description="Reasoning for this score")
    cited_evidence: List[str] = Field(description="Evidence IDs/locations used")
    timestamp: datetime = Field(default_factory=datetime.now)


# ===== CHIEF JUSTICE OUTPUT =====

class CriterionResult(BaseModel):
    """Final result for a single rubric criterion"""
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = Field(
        default=None,
        description="Explanation when judges disagree (variance > 2)"
    )
    remediation: str = Field(description="Specific file-level instructions")


class AuditReport(BaseModel):
    """Complete audit report"""
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult]
    remediation_plan: str
    generated_at: datetime = Field(default_factory=datetime.now)


# ===== GRAPH STATE (WITH REDUCERS) =====

class AgentState(TypedDict):
    """State passed through the LangGraph
    
    Uses reducers to prevent data overwriting in parallel execution:
    - operator.add: Appends to lists
    - operator.ior: Updates dicts (merge)
    """
    # Input
    repo_url: str
    pdf_path: str
    
    # Rubric (load from JSON)
    rubric_dimensions: List[Dict]
    
    # Evidence collection - uses ior to merge dicts from parallel detectives
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    
    # Judicial opinions - uses add to collect from parallel judges
    opinions: Annotated[List[JudicialOpinion], operator.add]
    
    # Final output
    final_report: Optional[AuditReport]
    
    # Error tracking
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]