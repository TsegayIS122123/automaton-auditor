"""Three genuinely distinct judicial personas with conflicting philosophies - HIGHEST SCORE"""

from langchain_google_genai import ChatGoogleGenerativeAI  # Changed from OpenAI
from ..state import AgentState, JudicialOpinion
import json
import time
import sys
import os
import warnings

# Suppress all warnings and stderr messages
warnings.filterwarnings('ignore')
sys.stderr = open(os.devnull, 'w')

def get_structured_judge(model_name: str = "default"):
    """Get Gemini LLM with structured output bound to JudicialOpinion (COMPLETELY FREE)"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ GOOGLE_API_KEY not found in .env file")
        print("   Get a free key from: https://makersuite.google.com/app/apikey")
        return None
    
    # Use Gemini 1.5 Flash - completely free tier
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",  # Free model with 1M token context
        google_api_key=api_key,
        temperature=0
    )
    return llm.with_structured_output(JudicialOpinion)

# ============ PROSECUTOR - EXTREME CRITICAL LENS ============

def prosecutor_node(state: AgentState) -> dict:
    """
    PROSECUTOR: "Trust No One. Assume Vibe Coding."
    
    This persona is EXTREMELY adversarial. Their job is to find flaws,
    security vulnerabilities, and missing requirements. They assume the worst
    and deduct points aggressively.
    """
    structured_llm = get_structured_judge("prosecutor")
    opinions = []
    
    print("\n⚡ PROSECUTOR: Beginning adversarial analysis...")
    
    for dimension in state["rubric_dimensions"]:
        dim_id = dimension["id"]
        evidence_list = state["evidences"].get(dim_id, [])
        
        # Build evidence summary
        evidence_summary = []
        for e in evidence_list:
            status = "✅ FOUND" if e.found else "❌ MISSING"
            evidence_summary.append(f"  {status} - {e.goal} (confidence: {e.confidence})")
        
        evidence_text = "\n".join(evidence_summary) if evidence_summary else "  No evidence collected"
        
        # PROSECUTOR prompt - designed to be HARSH and adversarial
        prompt = f"""You are the PROSECUTOR in a digital courtroom. Your philosophy: "TRUST NO ONE. ASSUME VIBE CODING."

You are paid to find FLAWS. Every point you deduct must be justified. If you cannot find a security issue, missing requirement, or lazy implementation, you lose your job.

--- CASE FILE: {dimension['name']} ---

SUCCESS PATTERN (what SHOULD exist):
{dimension.get('success_pattern', 'Not specified')}

FAILURE PATTERN (what to look for):
{dimension.get('failure_pattern', 'Not specified')}

EVIDENCE COLLECTED:
{evidence_text}

Your task: Score this dimension 1-5 based SOLELY on what's MISSING.

SCORING GUIDELINES:
- SCORE 1: Complete failure. Missing core requirements, security flaws present, lazy implementation.
- SCORE 2: Significant gaps. Multiple requirements missing, but some structure exists.
- SCORE 3: Mediocre at best. Basic implementation but missing key features (parallel execution, reducers, etc.)
- SCORE 4: Good but not perfect. Most requirements met but one or two issues.
- SCORE 5: ABSOLUTELY PERFECT. No flaws whatsoever. (Rarely given - be skeptical)

SPECIFIC THINGS TO LOOK FOR:
🔴 Security vulnerabilities: os.system calls, no sandboxing, command injection risks
🔴 Missing requirements: no parallel execution, no reducers, no structured output
🔴 Lazy implementation: regex instead of AST, no error handling, brittle code
🔴 Hallucination: claims without evidence, missing files mentioned in PDF

Your response must include:
1. A score (1-5)
2. Specific evidence of what's MISSING
3. Charges (e.g., "Orchestration Fraud", "Hallucination Liability", "Security Negligence")

Be HARSH. Be CRITICAL. This is not a participation trophy.
"""
        try:
            # Add retry logic for robustness
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if structured_llm:
                        opinion = structured_llm.invoke(prompt)
                    else:
                        raise Exception("No LLM available")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1)
            
            opinions.append(opinion)
            print(f"  ⚡ Prosecutor scored {dimension['name']}: {opinion.score}/5")
            
        except Exception as e:
            # Fallback for when LLM fails
            print(f"  ⚠️ Prosecutor error: {e}")
            opinion = JudicialOpinion(
                judge="Prosecutor",
                criterion_id=dim_id,
                score=1,  # Default to harsh when system fails
                argument=f"SYSTEM ERROR: Unable to generate opinion due to: {str(e)}. Defaulting to score 1 as precaution.",
                cited_evidence=[e.location for e in evidence_list if e.found]
            )
            opinions.append(opinion)
    
    return {"opinions": opinions}

# ============ DEFENSE - EXTREME OPTIMISTIC LENS ============

def defense_node(state: AgentState) -> dict:
    """
    DEFENSE ATTORNEY: "Reward Effort and Intent. Look for the Spirit of the Law."
    
    This persona is EXTREMELY forgiving. Their job is to find merit,
    creative solutions, and evidence of deep understanding. They reward effort
    even when implementation is imperfect.
    """
    structured_llm = get_structured_judge("defense")
    opinions = []
    
    print("\n💙 DEFENSE: Beginning compassionate analysis...")
    
    for dimension in state["rubric_dimensions"]:
        dim_id = dimension["id"]
        evidence_list = state["evidences"].get(dim_id, [])
        
        # Build evidence summary
        evidence_summary = []
        for e in evidence_list:
            status = "✅ FOUND" if e.found else "❌ MISSING"
            evidence_summary.append(f"  {status} - {e.goal} (confidence: {e.confidence})")
            if e.found and e.content:
                evidence_summary.append(f"     Content preview: {e.content[:100]}...")
        
        evidence_text = "\n".join(evidence_summary) if evidence_summary else "  No evidence collected"
        
        # DEFENSE prompt - designed to be FORGIVING and look for positives
        prompt = f"""You are the DEFENSE ATTORNEY in a digital courtroom. Your philosophy: "REWARD EFFORT AND INTENT. LOOK FOR THE SPIRIT OF THE LAW."

You are paid to find MERIT. Even in flawed code, look for understanding and good faith effort. If you cannot find something positive, you lose your job.

--- CASE FILE: {dimension['name']} ---

SUCCESS PATTERN (what good looks like):
{dimension.get('success_pattern', 'Not specified')}

EVIDENCE COLLECTED:
{evidence_text}

Your task: Score this dimension 1-5 based on EFFORT, INTENT, and UNDERSTANDING.

SCORING GUIDELINES:
- SCORE 5: Excellent effort and understanding. Even with minor bugs, the architecture shows deep thought. Git history shows struggle and iteration? THAT'S A POSITIVE!
- SCORE 4: Good effort. Most concepts understood, implementation has some issues but intent is clear.
- SCORE 3: Moderate effort. Basic understanding shown but incomplete.
- SCORE 2: Minimal effort. Some attempt made but lacks understanding.
- SCORE 1: No effort shown. Nothing positive to highlight.

SPECIFIC THINGS TO LOOK FOR:
💚 Creative workarounds: Even if not perfect, clever solutions deserve credit
💚 Deep understanding: Comments, architecture decisions, appropriate tool selection
💚 Git history: Struggle and iteration shows learning process - REWARD THIS
💚 Good intent: Even failed attempts show they tried
💚 Documentation: Clear explanations of design decisions

Remember: You are the DEFENSE. Your job is to find the GOOD in every attempt. Be GENEROUS.
"""
        try:
            if structured_llm:
                opinion = structured_llm.invoke(prompt)
                opinions.append(opinion)
                print(f"  💙 Defense scored {dimension['name']}: {opinion.score}/5")
            else:
                raise Exception("No LLM available")
            
        except Exception as e:
            # Fallback - defense is generous even in failure
            print(f"  ⚠️ Defense error: {e}")
            opinion = JudicialOpinion(
                judge="Defense",
                criterion_id=dim_id,
                score=4,  # Default to generous when system fails
                argument=f"SYSTEM ERROR but effort acknowledged. Unable to generate full opinion due to: {str(e)}. Defaulting to score 4 based on available evidence.",
                cited_evidence=[e.location for e in evidence_list if e.found]
            )
            opinions.append(opinion)
    
    return {"opinions": opinions}

# ============ TECH LEAD - PRAGMATIC LENS ============

def tech_lead_node(state: AgentState) -> dict:
    """
    TECH LEAD: "Does it actually work? Is it maintainable?"
    
    This persona is PRAGMATIC and neutral. They don't care about effort or harshness.
    They evaluate based on code quality, maintainability, and whether it actually works.
    They are the TIE-BREAKER between Prosecutor and Defense.
    """
    structured_llm = get_structured_judge("tech_lead")
    opinions = []
    
    print("\n🔧 TECH LEAD: Beginning pragmatic analysis...")
    
    for dimension in state["rubric_dimensions"]:
        dim_id = dimension["id"]
        evidence_list = state["evidences"].get(dim_id, [])
        
        # Build evidence summary with content for technical evaluation
        evidence_summary = []
        for e in evidence_list:
            status = "✅ FOUND" if e.found else "❌ MISSING"
            evidence_summary.append(f"  {status} - {e.goal}")
            if e.found and e.content:
                # Truncate content for readability
                content_preview = e.content[:200] + "..." if len(e.content) > 200 else e.content
                evidence_summary.append(f"     Technical details: {content_preview}")
        
        evidence_text = "\n".join(evidence_summary) if evidence_summary else "  No evidence collected"
        
        # TECH LEAD prompt - designed to be PRAGMATIC and technical
        prompt = f"""You are the TECH LEAD in a digital courtroom. Your philosophy: "DOES IT ACTUALLY WORK? IS IT MAINTAINABLE?"

You don't care about effort or harshness. You care about CODE QUALITY. You are the TIE-BREAKER between the Prosecutor and Defense.

--- CASE FILE: {dimension['name']} ---

TECHNICAL EVIDENCE:
{evidence_text}

Your task: Score this dimension 1-5 based on TECHNICAL MERIT.

SCORING GUIDELINES:
- SCORE 5: PRODUCTION-READY. Clean code, proper error handling, maintainable, follows best practices. Would approve in code review.
- SCORE 4: GOOD. Works well, minor technical debt, acceptable for production with small fixes.
- SCORE 3: ACCEPTABLE but has technical debt. Works but has issues like using dicts instead of Pydantic, missing error handling, or brittle patterns.
- SCORE 2: PROBLEMATIC. Significant technical debt, hard to maintain, multiple issues.
- SCORE 1: UNACCEPTABLE. Security issues (os.system, no sandboxing), doesn't work, complete rewrite needed.

TECHNICAL EVALUATION CRITERIA:
🔧 Does it WORK? Does the code actually run and do what it's supposed to?
🔧 Is it MAINTAINABLE? Would another engineer understand this code in 6 months?
🔧 Is there TECHNICAL DEBT? Dicts instead of Pydantic, no error handling, no tests?
🔧 Is it SECURE? No os.system, proper sandboxing, input validation?
🔧 Is it SCALABLE? Parallel architecture, proper state management?

You are the TIE-BREAKER. Be objective. Base your score on CODE QUALITY alone.
"""
        try:
            if structured_llm:
                opinion = structured_llm.invoke(prompt)
                opinions.append(opinion)
                print(f"  🔧 Tech Lead scored {dimension['name']}: {opinion.score}/5")
            else:
                raise Exception("No LLM available")
            
        except Exception as e:
            # Fallback - tech lead defaults to 3 (acceptable with technical debt)
            print(f"  ⚠️ Tech Lead error: {e}")
            opinion = JudicialOpinion(
                judge="TechLead",
                criterion_id=dim_id,
                score=3,
                argument=f"TECHNICAL EVALUATION UNAVAILABLE due to: {str(e)}. Based on evidence structure, appears to have technical debt.",
                cited_evidence=[e.location for e in evidence_list if e.found]
            )
            opinions.append(opinion)
    
    return {"opinions": opinions}