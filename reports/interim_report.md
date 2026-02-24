# Automaton Auditor - Interim Report

**Date:** February 25, 2026
**Author:** Tsegay
**GitHub:** https://github.com/TsegayIS122123/automaton-auditor

## 1. Executive Summary

This interim report documents the architecture and implementation progress of the Automaton Auditor, a multi-agent LangGraph system for autonomous code audit. The system implements a "digital courtroom" architecture with parallel detective agents and dialectical judicial synthesis.

## 2. Architecture Decisions

### 2.1 Why Pydantic over Dicts?
We chose Pydantic BaseModel for all state definitions because:
- **Type Safety**: Runtime validation prevents corrupted state
- **Structured Output**: Enables `.with_structured_output()` for judges
- **Reducers**: `operator.add` and `operator.ior` enable parallel safety
- **Documentation**: Self-documenting schemas with Field descriptions

### 2.2 AST Parsing Strategy
We implemented AST-based analysis (not regex) because:
- **Accuracy**: Detects actual code structure, not string matches
- **Depth**: Can verify if StateGraph is instantiated vs just mentioned
- **Reliability**: Immune to comment/spacing variations

### 2.3 Sandboxing Strategy
All git operations run in `tempfile.TemporaryDirectory()`:
- **Security**: No risk of host system contamination
- **Cleanup**: Automatic removal even on failure
- **Isolation**: Each audit gets fresh environment

### 2.4 PDF Processing (RAG-lite)
Implemented ChromaDB with sentence-transformers:
- **Chunking**: 500-word overlapping chunks
- **Embeddings**: all-MiniLM-L6-v2 model
- **Query**: Semantic search for concepts, not full-text dump

## 3. Implementation Progress

### 3.1 Completed Features ✓
- [x] Pydantic state models with reducers
- [x] Sandboxed git clone with tempfile
- [x] AST parser for graph structure
- [x] Git history forensic analysis
- [x] PDF text extraction and chunking
- [x] ChromaDB vector store setup
- [x] RAG-lite concept querying
- [x] RepoInvestigator node
- [x] DocAnalyst node
- [x] EvidenceAggregator node
- [x] Partial graph with fan-out/fan-in

### 3.2 In Progress ���
- [ ] VisionInspector node (implementation ready)
- [ ] Three judge personas with structured output
- [ ] Chief Justice synthesis engine
- [ ] Deterministic conflict resolution rules

## 4. Known Gaps & Mitigation Plan

| Gap | Impact | Mitigation | Timeline |
|-----|--------|------------|----------|
| VisionInspector not integrated | Missing diagram analysis | Implement by Saturday | Day 5-6 |
| Judge prompts need refinement | May lack genuine conflict | Test with adversarial examples | Day 6 |
| Synthesis rules not coded | Risk of LLM averaging | Hardcode deterministic logic | Day 7 |

## 5. Architecture Diagrams

### 5.1 Detective Layer Flow
START → [RepoInvestigator, DocAnalyst] (parallel) → EvidenceAggregator → END


### 5.2 Planned Full Architecture
START → Detectives (parallel) → Aggregator → Judges (parallel) → Chief Justice → END

### 5.3 State Management
```python
class AgentState(TypedDict):
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]  # Parallel merge
    opinions: Annotated[List[JudicialOpinion], operator.add]      # Parallel append

6. LangSmith Integration
We've integrated LangSmith for full observability:

Trace Link: https://smith.langchain.com/public/...

Key Insights: Detective parallel execution visible, evidence aggregation confirmed

7. Conclusion
The foundation is solid with all detective-layer components complete. The remaining judicial layer implementation is on track for final submission.
