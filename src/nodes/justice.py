"""Chief Justice node with hardcoded deterministic conflict resolution rules"""

from ..state import AgentState, AuditReport, CriterionResult, JudicialOpinion
from datetime import datetime
import json

def chief_justice_node(state: AgentState) -> dict:
    """
    Synthesizes judge opinions using hardcoded deterministic rules.
    NOT just averaging - applies constitution rules from rubric.
    """
    rubric = state["rubric_dimensions"]
    opinions = state["opinions"]
    evidences = state["evidences"]
    
    criteria_results = []
    
    # Group opinions by dimension
    for dimension in rubric:
        dim_id = dimension["id"]
        dim_opinions = [o for o in opinions if o.criterion_id == dim_id]
        
        if not dim_opinions:
            continue
        
        # Extract scores
        scores = [o.score for o in dim_opinions]
        prosecutor = next((o for o in dim_opinions if o.judge == "Prosecutor"), None)
        defense = next((o for o in dim_opinions if o.judge == "Defense"), None)
        tech = next((o for o in dim_opinions if o.judge == "TechLead"), None)
        
        # RULE 1: Security Override
        security_override = False
        if prosecutor and any(term in prosecutor.argument.lower() for term in ["security", "vulnerability", "os.system", "injection"]):
            security_override = True
        
        # RULE 2: Fact Supremacy
        fact_override = False
        if defense and "deep metacognition" in defense.argument.lower():
            # Check if evidence supports this claim
            has_deep_evidence = any(
                ev.dimension_id == "theoretical_depth" and ev.found 
                for ev in evidences.get("doc", [])
            )
            if not has_deep_evidence:
                fact_override = True
        
        # Calculate final score with rules
        if security_override:
            final_score = min(3, max(scores))
            dissent = f"Security override applied: {prosecutor.argument[:100]}..."
        elif fact_override:
            final_score = tech.score if tech else max(scores)
            dissent = f"Fact supremacy: Defense claim of deep understanding not supported by evidence"
        elif dim_id == "graph_orchestration" and tech:
            # RULE 3: Functionality weight for architecture
            final_score = tech.score
            dissent = "Tech Lead opinion weighted highest for architecture criterion"
        else:
            # Default: median score (not average - more robust)
            sorted_scores = sorted(scores)
            final_score = sorted_scores[len(sorted_scores)//2]
            dissent = None
        
        # Check variance for dissent requirement
        if max(scores) - min(scores) > 2:
            dissent = f"Disagreement: Prosecutor={prosecutor.score if prosecutor else 'N/A'}, Defense={defense.score if defense else 'N/A'}, Tech={tech.score if tech else 'N/A'}"
        
        # Generate remediation
        remediation = generate_remediation(dim_id, final_score, evidences)
        
        criteria_results.append(CriterionResult(
            dimension_id=dim_id,
            dimension_name=dimension["name"],
            final_score=final_score,
            judge_opinions=dim_opinions,
            dissent_summary=dissent,
            remediation=remediation
        ))
    
    # Generate final report
    report = AuditReport(
        repo_url=state["repo_url"],
        executive_summary=generate_executive_summary(criteria_results),
        overall_score=sum(c.final_score for c in criteria_results) / len(criteria_results),
        criteria=criteria_results,
        remediation_plan=generate_remediation_plan(criteria_results)
    )
    
    # Serialize to Markdown
    markdown = render_markdown_report(report)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"audit/report_onself_generated/audit_report_{timestamp}.md"
    
    import os
    os.makedirs("audit/report_onself_generated", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    return {"final_report": report}

def generate_remediation(dim_id: str, score: int, evidences: dict) -> str:
    """Generate specific file-level remediation instructions"""
    if score >= 4:
        return "No major issues found. Maintain current implementation."
    
    remediation_map = {
        "git_forensic_analysis": "Add more granular commits showing progression from setup to tools to graph. Current commit history lacks clear iterative development.",
        "state_management_rigor": "Implement Pydantic models with operator.add/ior reducers in src/state.py. Ensure Evidence and JudicialOpinion classes exist.",
        "graph_orchestration": "Add parallel fan-out/fan-in pattern in src/graph.py. Ensure START branches to multiple detectives and aggregator collects results.",
        "safe_tool_engineering": "Use tempfile.TemporaryDirectory() and subprocess.run() instead of os.system. Add error handling around all external calls.",
        "structured_output_enforcement": "Add .with_structured_output() to judge nodes in src/nodes/judges.py bound to JudicialOpinion schema.",
        "judicial_nuance": "Create three distinct judge personas with conflicting prompts in src/nodes/judges.py. Ensure prompts differ by >50%.",
        "chief_justice_synthesis": "Implement hardcoded deterministic rules in src/nodes/justice.py, not LLM averaging. Include security override and fact supremacy.",
        "theoretical_depth": "Enhance PDF report with detailed explanations of Dialectical Synthesis, Fan-In/Fan-Out, and Metacognition with code examples.",
        "report_accuracy": "Ensure all file paths mentioned in PDF report actually exist in repository. Remove hallucinated paths.",
        "swarm_visual": "Add clear architecture diagram showing parallel fan-out/fan-in for both detectives and judges."
    }
    
    return remediation_map.get(dim_id, f"Review implementation of {dim_id} against rubric requirements and improve accordingly.")

def generate_executive_summary(criteria: list) -> str:
    """Generate executive summary"""
    avg_score = sum(c.final_score for c in criteria) / len(criteria)
    strengths = [c.dimension_name for c in criteria if c.final_score >= 4]
    weaknesses = [c.dimension_name for c in criteria if c.final_score <= 2]
    
    summary = f"## Executive Summary\n\n"
    summary += f"**Overall Score: {avg_score:.1f}/5**\n\n"
    
    if strengths:
        summary += f"### Strengths\n"
        for s in strengths:
            summary += f"- ✅ {s}\n"
        summary += "\n"
    
    if weaknesses:
        summary += f"### Areas for Improvement\n"
        for w in weaknesses:
            summary += f"- ⚠️ {w}\n"
        summary += "\n"
    
    return summary

def generate_remediation_plan(criteria: list) -> str:
    """Generate comprehensive remediation plan"""
    plan = "## Remediation Plan\n\n"
    
    for c in criteria:
        if c.final_score < 4:
            plan += f"### {c.dimension_name}\n"
            plan += f"{c.remediation}\n\n"
    
    return plan

def render_markdown_report(report: AuditReport) -> str:
    """Render report as Markdown"""
    md = f"""# Automaton Auditor - Final Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Repository:** {report.repo_url}

{report.executive_summary}

## Criterion Breakdown
"""
    for i, c in enumerate(report.criteria, 1):
        md += f"""
### {i}. {c.dimension_name}
**Final Score: {c.final_score}/5**

**The Debate:**
"""
        for o in c.judge_opinions:
            md += f"- **{o.judge}**: {o.argument} (Score: {o.score})\n"
        
        if c.dissent_summary:
            md += f"\n**Dissent:** {c.dissent_summary}\n"
        
        md += f"\n**Remediation:** {c.remediation}\n"
        md += "---\n"
    
    md += f"\n{report.remediation_plan}"
    return md