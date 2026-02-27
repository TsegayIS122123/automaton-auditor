"""Judge nodes with distinct personas using structured output"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from ..state import AgentState, JudicialOpinion
import os

def get_llm():
    """Get LLM based on available API keys"""
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    return ChatOpenAI(model="gpt-4", temperature=0)

def prosecutor_node(state: AgentState) -> dict:
    """
    The Prosecutor - Critical Lens
    "Trust No One. Assume Vibe Coding."
    """
    llm = get_llm().with_structured_output(JudicialOpinion)
    opinions = []
    
    for dimension in state["rubric_dimensions"]:
        evidence_list = state["evidences"].get(dimension["id"], [])
        
        prompt = f"""You are the PROSECUTOR. Your job is to be HARSH and find flaws.

Dimension ID: {dimension['id']}
Dimension Name: {dimension['name']}
Success Pattern: {dimension.get('success_pattern', 'N/A')}
Failure Pattern: {dimension.get('failure_pattern', 'N/A')}

Evidence Collected:
{chr(10).join([f'- {e.goal}: Found={e.found}, Confidence={e.confidence}, Rationale={e.rationale}' for e in evidence_list])}

Instructions:
- Score 1-2: Clear failures, missing requirements, security flaws
- Score 3-4: Mediocre implementation, some issues present
- Score 5: Only if absolutely perfect with no flaws
- Look for: missing files, no parallel execution, os.system calls, no structured output
- If evidence shows linear pipeline instead of parallel, charge "Orchestration Fraud"
- If judges return freeform text, charge "Hallucination Liability"

Provide a harsh score and list specific missing elements.
"""
        opinion = llm.invoke(prompt)
        opinions.append(opinion)
    
    return {"opinions": opinions}

def defense_node(state: AgentState) -> dict:
    """
    The Defense Attorney - Optimistic Lens
    "Reward Effort and Intent. Look for the Spirit of the Law."
    """
    llm = get_llm().with_structured_output(JudicialOpinion)
    opinions = []
    
    for dimension in state["rubric_dimensions"]:
        evidence_list = state["evidences"].get(dimension["id"], [])
        
        prompt = f"""You are the DEFENSE ATTORNEY. Your job is to be GENEROUS and reward effort.

Dimension ID: {dimension['id']}
Dimension Name: {dimension['name']}
Success Pattern: {dimension.get('success_pattern', 'N/A')}

Evidence Collected:
{chr(10).join([f'- {e.goal}: Found={e.found}, Confidence={e.confidence}, Rationale={e.rationale}' for e in evidence_list])}

Instructions:
- Score 3-5: Even with minor bugs, reward good intent
- Score 1-2: Only if absolutely nothing works
- Look for creative workarounds and deep understanding
- Git history showing struggle and iteration is a POSITIVE
- If code is buggy but architecture report shows deep understanding, argue for higher score
- Effort matters more than perfection

Provide a generous score and highlight strengths.
"""
        opinion = llm.invoke(prompt)
        opinions.append(opinion)
    
    return {"opinions": opinions}

def tech_lead_node(state: AgentState) -> dict:
    """
    The Tech Lead - Pragmatic Lens
    "Does it actually work? Is it maintainable?"
    """
    llm = get_llm().with_structured_output(JudicialOpinion)
    opinions = []
    
    for dimension in state["rubric_dimensions"]:
        evidence_list = state["evidences"].get(dimension["id"], [])
        
        prompt = f"""You are the TECH LEAD. Your job is to be PRAGMATIC and assess viability.

Dimension ID: {dimension['id']}
Dimension Name: {dimension['name']}

Evidence Collected:
{chr(10).join([f'- {e.goal}: Found={e.found}, Content={e.content[:200]}...' for e in evidence_list])}

Questions to answer:
1. Does this actually WORK? (Functionality)
2. Is it MAINTAINABLE? (Code quality, documentation)
3. Is there technical debt? (Pydantic vs dicts, error handling)
4. Would you approve this in a production code review?

Standards:
- If using plain dicts instead of Pydantic: Ruling = "Technical Debt", Score 3
- If using os.system without sandboxing: Ruling = "Security Negligence", Score 1
- If parallel architecture implemented: Higher score
- You are the TIE-BREAKER between Prosecutor and Defense

Provide a realistic score (1, 3, or 5) and technical remediation advice.
"""
        opinion = llm.invoke(prompt)
        opinions.append(opinion)
    
    return {"opinions": opinions}