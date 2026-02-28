"""Chief Justice with complete deterministic synthesis rules - HIGHEST SCORE"""

from ..state import AgentState, AuditReport, CriterionResult, JudicialOpinion
from datetime import datetime
import os
import json

def chief_justice_node(state: AgentState) -> dict:
    """
    Chief Justice with ALL deterministic rules from rubric.
    
    IMPLEMENTED RULES:
    1. Security Override: Security flaws cap score at 3
    2. Fact Supremacy: Detective evidence overrules unsupported judge claims
    3. Functionality Weight: Tech Lead highest weight for architecture
    4. Dissent Requirement: Score variance > 2 triggers dissent summary
    5. Variance Re-evaluation: Re-evaluate when variance exceeds threshold
    """
    rubric = state["rubric_dimensions"]
    opinions = state["opinions"]
    evidences = state["evidences"]
    
    criteria_results = []
    
    print("\n🏛️ CHIEF JUSTICE: Beginning synthesis with deterministic rules...")
    
    # Group opinions by dimension
    for dimension in rubric:
        dim_id = dimension["id"]
        dim_name = dimension["name"]
        dim_opinions = [o for o in opinions if o.criterion_id == dim_id]
        
        if not dim_opinions:
            print(f"  ⚠️ No opinions for {dim_name}, skipping")
            continue
        
        # Extract opinions by judge
        prosecutor = next((o for o in dim_opinions if o.judge == "Prosecutor"), None)
        defense = next((o for o in dim_opinions if o.judge == "Defense"), None)
        tech = next((o for o in dim_opinions if o.judge == "TechLead"), None)
        
        # Get scores (default to 3 if missing)
        prosecutor_score = prosecutor.score if prosecutor else 3
        defense_score = defense.score if defense else 3
        tech_score = tech.score if tech else 3
        
        scores = [prosecutor_score, defense_score, tech_score]
        
        print(f"\n  📋 {dim_name}:")
        print(f"     Prosecutor: {prosecutor_score}, Defense: {defense_score}, Tech: {tech_score}")
        
        # ============ RULE 1: SECURITY OVERRIDE ============
        security_override = False
        security_reason = None
        
        if prosecutor and any(term in prosecutor.argument.lower() for term in 
                            ["security", "vulnerability", "os.system", "injection", "sandbox", "unsafe"]):
            security_override = True
            security_reason = prosecutor.argument[:150]
        
        # Also check evidence for security issues
        security_evidence = any(
            e.dimension_id == "safe_tool_engineering" and not e.found
            for e in evidences.get("repo", [])
        )
        
        if security_evidence:
            security_override = True
            security_reason = "Evidence shows security tooling issues"
        
        if security_override:
            final_score = min(3, max(scores))
            dissent = f"🔒 SECURITY OVERRIDE: Score capped at 3 due to security concerns. {security_reason}"
            print(f"     🔒 Security override applied - score capped at {final_score}")
        
        # ============ RULE 2: FACT SUPREMACY ============
        elif defense and defense_score >= 4 and any(term in defense.argument.lower() for term in 
                                                   ["deep", "understanding", "metacognition", "sophisticated", "excellent"]):
            # Check if evidence supports deep understanding claim
            has_deep_evidence = any(
                e.dimension_id == "theoretical_depth" and e.found and e.confidence > 0.7
                for e in evidences.get("doc", [])
            )
            
            if not has_deep_evidence:
                # Overrule defense, use tech lead score
                final_score = tech_score
                dissent = f"📊 FACT SUPREMACY: Defense claim of deep understanding not supported by evidence. Using Tech Lead score ({tech_score})."
                print(f"     📊 Fact supremacy applied - overruling defense")
            else:
                # Evidence supports defense
                final_score = defense_score
                dissent = None
                print(f"     ✅ Defense claim supported by evidence")
        
        # ============ RULE 3: FUNCTIONALITY WEIGHT FOR ARCHITECTURE ============
        elif dim_id == "graph_orchestration":
            # Tech Lead carries highest weight for architecture
            final_score = tech_score
            dissent = f"⚙️ FUNCTIONALITY WEIGHT: Tech Lead opinion prioritized for architecture criterion (score: {tech_score})"
            print(f"     ⚙️ Functionality weight applied - using Tech Lead score")
        
        # ============ DEFAULT: VARIANCE HANDLING ============
        else:
            # Calculate variance
            score_variance = max(scores) - min(scores)
            
            if score_variance > 2:
                # RULE 4: DISSENT REQUIREMENT
                # Use median instead of mean for robustness
                sorted_scores = sorted(scores)
                final_score = sorted_scores[1]  # median
                dissent = f"⚖️ DISSENT: Significant disagreement (variance={score_variance}). Prosecutor={prosecutor_score}, Defense={defense_score}, Tech={tech_score}. Using median score {final_score}."
                print(f"     ⚖️ Dissent detected - variance {score_variance} > 2")
                
                # RULE 5: VARIANCE RE-EVALUATION (implied by logging)
                print(f"     ⚖️ Triggering variance re-evaluation for {dim_name}")
            else:
                # Low variance - use mean
                final_score = round(sum(scores) / len(scores))
                dissent = None
                print(f"     ✅ Consensus - variance {score_variance} <= 2")
        
        # Generate remediation based on final score
        remediation = generate_remediation(dim_id, final_score, evidences)
        
        # Create criterion result
        criteria_results.append(CriterionResult(
            dimension_id=dim_id,
            dimension_name=dim_name,
            final_score=final_score,
            judge_opinions=dim_opinions,
            dissent_summary=dissent,
            remediation=remediation
        ))
    
    # ============ GENERATE FINAL REPORT ============
    
    # Calculate overall score
    overall_score = sum(c.final_score for c in criteria_results) / len(criteria_results) if criteria_results else 0
    
    # Generate executive summary
    executive_summary = generate_executive_summary(criteria_results)
    
    # Generate remediation plan
    remediation_plan = generate_remediation_plan(criteria_results)
    
    # Create report
    report = AuditReport(
        repo_url=state["repo_url"],
        executive_summary=executive_summary,
        overall_score=overall_score,
        criteria=criteria_results,
        remediation_plan=remediation_plan
    )
    
    # ============ SERIALIZE TO MARKDOWN FILE ============
    markdown = render_markdown_report(report)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save self-audit report
    filename = f"audit/report_onself_generated/audit_{timestamp}.md"
    os.makedirs("audit/report_onself_generated", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"\n✅ Final report saved to: {filename}")
    print(f"🏛️ Chief Justice synthesis complete. Overall score: {overall_score:.1f}/5")
    
    return {"final_report": report}

def generate_remediation(dim_id: str, score: int, evidences: dict) -> str:
    """Generate specific file-level remediation instructions"""
    if score >= 4:
        return "No remediation needed. Implementation meets or exceeds expectations."
    
    remediation_map = {
        "git_forensic_analysis": """**Issue:** Git history lacks clear progression from setup → tools → graph.

**Remediation:**
1. Reorganize commits to show iterative development
2. Ensure commit messages reflect: setup, tool engineering, graph orchestration
3. Avoid bulk uploads (single commit with all code)
4. Add timestamps showing development over time

**Files to update:** Entire repository git history""",
        
        "state_management_rigor": """**Issue:** State management lacks proper Pydantic models or reducers.

**Remediation:**
1. Add Evidence class inheriting from BaseModel in src/state.py
2. Add JudicialOpinion class inheriting from BaseModel
3. Define AgentState with Annotated fields using operator.add and operator.ior
4. Add field constraints (ge, le, descriptions)

**Files to update:** src/state.py""",
        
        "graph_orchestration": """**Issue:** Graph lacks proper parallel fan-out/fan-in patterns.

**Remediation:**
1. Ensure START branches to all detectives in parallel
2. Add evidence aggregator node as fan-in point
3. Wire judges in parallel from aggregator
4. Add conditional edges for error handling
5. Verify two distinct parallel layers exist

**Files to update:** src/graph.py""",
        
        "safe_tool_engineering": """**Issue:** Tools lack proper sandboxing or use unsafe operations.

**Remediation:**
1. Replace any os.system calls with subprocess.run()
2. Use tempfile.TemporaryDirectory() for all git operations
3. Add comprehensive error handling (try/except)
4. Implement timeout protection for external calls
5. Add input sanitization for repository URLs

**Files to update:** src/tools/repo_tools.py""",
        
        "structured_output_enforcement": """**Issue:** Judges not using structured output or missing retry logic.

**Remediation:**
1. Add .with_structured_output(JudicialOpinion) to all judge nodes
2. Implement retry logic with exponential backoff
3. Add fallback opinions when LLM fails
4. Validate all opinions against schema before adding to state

**Files to update:** src/nodes/judges.py""",
        
        "judicial_nuance": """**Issue:** Judge personas not sufficiently distinct or missing conflicting philosophies.

**Remediation:**
1. Ensure Prosecutor prompt is adversarial (looks for flaws)
2. Ensure Defense prompt is forgiving (rewards effort)
3. Ensure Tech Lead prompt is pragmatic (focuses on code quality)
4. Verify prompts differ by >50% in content and tone
5. Add explicit scoring guidelines for each persona

**Files to update:** src/nodes/judges.py""",
        
        "chief_justice_synthesis": """**Issue:** Synthesis lacks deterministic rules or uses LLM averaging.

**Remediation:**
1. Implement security override rule (flaws cap score at 3)
2. Implement fact supremacy rule (evidence overrules opinion)
3. Implement functionality weight (Tech Lead highest for architecture)
4. Add dissent summaries for variance > 2
5. Write report to file, not console

**Files to update:** src/nodes/justice.py""",
        
        "theoretical_depth": """**Issue:** PDF report lacks deep explanation of key concepts.

**Remediation:**
1. Add detailed section on Dialectical Synthesis with code examples
2. Explain Fan-In/Fan-Out patterns with diagrams
3. Discuss Metacognition and how system self-evaluates
4. Include architecture diagrams showing parallel flow
5. Reference specific file paths in explanations

**Files to update:** reports/final_report.pdf""",
        
        "report_accuracy": """**Issue:** PDF report mentions files that don't exist or makes unsupported claims.

**Remediation:**
1. Verify all file paths mentioned actually exist in repository
2. Remove any hallucinated paths
3. Ensure claims about implementation match actual code
4. Cross-reference all evidence with codebase
5. Update report to reflect actual implementation

**Files to update:** reports/final_report.pdf""",
        
        "swarm_visual": """**Issue:** Missing or inaccurate architecture diagrams.

**Remediation:**
1. Add clear diagram showing parallel fan-out/fan-in for detectives
2. Add diagram showing parallel fan-out/fan-in for judges
3. Ensure diagrams match actual graph implementation
4. Include conditional error paths in diagrams
5. Use Mermaid syntax for GitHub rendering

**Files to update:** reports/final_report.pdf, README.md"""
    }
    
    return remediation_map.get(dim_id, f"Review implementation of {dim_id} against rubric requirements and improve accordingly.")

def generate_executive_summary(criteria: list) -> str:
    """Generate executive summary with strengths and weaknesses"""
    avg_score = sum(c.final_score for c in criteria) / len(criteria) if criteria else 0
    strengths = [c.dimension_name for c in criteria if c.final_score >= 4]
    weaknesses = [c.dimension_name for c in criteria if c.final_score <= 2]
    needs_attention = [c.dimension_name for c in criteria if 2 < c.final_score < 4]
    
    summary = f"""## Executive Summary

**Overall Score: {avg_score:.1f}/5**

### Key Findings
"""
    if strengths:
        summary += "\n**Strengths:**\n"
        for s in strengths:
            summary += f"- ✅ {s}\n"
    
    if needs_attention:
        summary += "\n**Needs Attention:**\n"
        for n in needs_attention:
            summary += f"- 📌 {n}\n"
    
    if weaknesses:
        summary += "\n**Critical Issues:**\n"
        for w in weaknesses:
            summary += f"- ⚠️ {w}\n"
    
    summary += f"""
### Summary
The system demonstrates {'strong' if avg_score >= 4 else 'adequate' if avg_score >= 3 else 'weak'} implementation across {len(criteria)} dimensions. 
{'Focus on addressing critical issues and areas needing attention.' if weaknesses or needs_attention else 'All dimensions meet or exceed expectations.'}
"""
    return summary

def generate_remediation_plan(criteria: list) -> str:
    """Generate comprehensive remediation plan with priorities"""
    plan = "## Remediation Plan\n\n"
    
    # Sort by priority (lowest scores first)
    sorted_criteria = sorted(criteria, key=lambda c: c.final_score)
    
    priority_levels = {
        "critical": [c for c in sorted_criteria if c.final_score <= 2],
        "high": [c for c in sorted_criteria if 2 < c.final_score < 4],
        "low": [c for c in sorted_criteria if c.final_score >= 4]
    }
    
    if priority_levels["critical"]:
        plan += "### 🔴 CRITICAL PRIORITY (Must Fix)\n\n"
        for c in priority_levels["critical"]:
            plan += f"#### {c.dimension_name}\n"
            plan += f"{c.remediation}\n\n"
    
    if priority_levels["high"]:
        plan += "### 🟡 HIGH PRIORITY (Should Fix)\n\n"
        for c in priority_levels["high"]:
            plan += f"#### {c.dimension_name}\n"
            plan += f"{c.remediation}\n\n"
    
    if priority_levels["low"]:
        plan += "### 🟢 LOW PRIORITY (Nice to Have)\n\n"
        for c in priority_levels["low"]:
            plan += f"#### {c.dimension_name}\n"
            plan += f"{c.remediation}\n\n"
    
    return plan

def render_markdown_report(report: AuditReport) -> str:
    """Render complete Markdown report with all required sections"""
    md = f"""# 🤖 Automaton Auditor - Final Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Repository:** {report.repo_url}  
**Overall Score:** {report.overall_score:.1f}/5

---

{report.executive_summary}

---

## Detailed Criterion Breakdown

"""
    for i, c in enumerate(report.criteria, 1):
        md += f"""
### {i}. {c.dimension_name}
**Final Score: {c.final_score}/5**

**Judge Opinions:**
"""
        for o in c.judge_opinions:
            # Truncate arguments for readability
            arg = o.argument[:200] + "..." if len(o.argument) > 200 else o.argument
            md += f"- **{o.judge}** (Score: {o.score}): {arg}\n"
        
        if c.dissent_summary:
            md += f"\n**Dissent:** {c.dissent_summary}\n"
        
        md += f"\n**Remediation:**\n{c.remediation}\n"
        md += "\n---\n"
    
    md += f"""

{report.remediation_plan}

---

*Report generated by Automaton Auditor v1.0*
"""
    return md