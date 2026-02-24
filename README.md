# 🤖 Automaton Auditor
A multi-agent LangGraph swarm for autonomous code audit and governance. Digital courtroom architecture with parallel detectives and dialectical judges.

<div align="center">
  
  ![LangGraph](https://img.shields.io/badge/LangGraph-1.0-blue)
  ![Python](https://img.shields.io/badge/Python-3.10+-green)
  ![Pydantic](https://img.shields.io/badge/Pydantic-2.0-red)
  
  **A Multi-Agent System for Autonomous Code Audit & Governance**
  
  *"Digital Courtroom Architecture with Parallel Detectives and Dialectical Judges"*
  
</div>

---

## 📋 Overview

The Automaton Auditor is a production-grade **multi-agent system** built with LangGraph that autonomously audits GitHub repositories against complex rubrics. It implements a hierarchical "digital courtroom" architecture where specialized agents collaborate to produce forensic-grade audit reports.

This system addresses the scaling challenge in AI-Native Enterprises: **when 1000 agents generate code simultaneously, humans cannot manually review every PR**. The Automaton Auditor provides automated quality assurance at scale.

---
## 🏛️ Architecture: The Digital Courtroom

```mermaid
graph TB
    subgraph Input["📥 Input Layer"]
        A[GitHub Repository URL] --> Parser
        B[PDF Report] --> Parser
    end

    subgraph Detectives["🔍 Detective Layer (Parallel Investigation)"]
        direction TB
        RI[RepoInvestigator<br/>Git + AST Analysis] --> EviAgg
        DA[DocAnalyst<br/>PDF + RAG Analysis] --> EviAgg
        VI[VisionInspector<br/>Diagram Analysis] --> EviAgg
    end

    subgraph Evidence["📊 Evidence Aggregation"]
        EviAgg[Evidence Aggregator<br/>Synchronization Node] --> EvidenceStore[(Evidence Store)]
    end

    subgraph Judges["⚖️ Judicial Layer (Dialectical Debate)"]
        direction TB
        EvidenceStore --> Prosecutor
        EvidenceStore --> Defense
        EvidenceStore --> TechLead
        
        Prosecutor[Prosecutor<br/>Critical Lens] --> OpinionPool
        Defense[Defense<br/>Optimistic Lens] --> OpinionPool
        TechLead[Tech Lead<br/>Pragmatic Lens] --> OpinionPool
    end

    subgraph Synthesis["🏛️ Supreme Court"]
        OpinionPool --> ChiefJustice[Chief Justice<br/>Synthesis Engine]
        ChiefJustice --> Rules{Deterministic Rules}
        Rules --> Security[Security Override]
        Rules --> Fact[Fact Supremacy]
        Rules --> Function[Functionality Weight]
        Rules --> Dissent[Dissent Requirement]
    end

    subgraph Output["📄 Output Layer"]
        Synthesis --> Report[Audit Report<br/>Markdown]
        Report --> Executive[Executive Summary]
        Report --> Criteria[Criterion Breakdown]
        Report --> Remediation[Remediation Plan]
    end

    Parser --> Detectives
```

### 🔄 Parallel Execution Flow

The architecture implements **two layers of parallel processing**:

| Layer | Components | Pattern |
|-------|------------|---------|
| **Detective Layer** | RepoInvestigator, DocAnalyst, VisionInspector | Fan-out → Aggregate |
| **Judicial Layer** | Prosecutor, Defense, TechLead | Fan-out → Synthesize |

### ⚖️ Dialectical Synthesis 

```mermaid
graph LR
    subgraph Thesis["Thesis (Prosecutor)"]
        A[Find Flaws<br/>Score: 1-2] --> Conflict
    end
    
    subgraph Antithesis["Antithesis (Defense)"]
        B[Find Merit<br/>Score: 4-5] --> Conflict
    end
    
    subgraph Conflict["Dialectical Conflict"]
        C{Score Variance > 2?}
    end
    
    subgraph Synthesis["Synthesis (Chief Justice)"]
        C -->|Yes| D[Trigger Dissent]
        C -->|No| E[Apply Rules]
        D --> F[Security Override]
        D --> G[Fact Supremacy]
        D --> H[Functionality Weight]
        E --> F
        E --> G
        E --> H
        F & G & H --> I[Final Verdict]
    end
```

---

## 🎯 Key Features

### 🔍 Forensic Detective Layer
- **RepoInvestigator**: AST-based code analysis (not regex) with git history forensics
- **DocAnalyst**: PDF parsing with RAG-lite architecture for targeted queries
- **VisionInspector**: Multimodal diagram analysis (optional but implemented)

### ⚖️ Dialectical Judicial Layer
- **Prosecutor**: Adversarial lens - finds flaws, gaps, and security issues
- **Defense**: Optimistic lens - rewards effort and creative solutions  
- **Tech Lead**: Pragmatic lens - evaluates maintainability and viability

### 🏛️ Supreme Court Synthesis
- **Deterministic conflict resolution** (not LLM averaging)
- **Security override rules** - vulnerabilities cap scores
- **Fact supremacy** - evidence overrides opinion
- **Dissent requirement** - explains score variance

### 🛡️ Production-Grade Infrastructure
- **Pydantic validation** throughout
- **State reducers** (`operator.add`, `operator.ior`) for parallel safety
- **Sandboxed execution** with tempfile isolation
- **LangSmith observability** for full traceability
- **uv package management** for dependency isolation

---
# 📂 Project Structure
```bash
automaton-auditor/
├── src/
│   ├── __init__.py
│   ├── state.py                 # Pydantic models with reducers
│   ├── graph.py                  # LangGraph state machine
│   ├── nodes/
│   │   ├── detectives.py         # Forensic collectors
│   │   ├── judges.py              # Three judicial personas
│   │   └── justice.py             # Chief Justice synthesis
│   └── tools/
│       ├── repo_tools.py          # Git + AST analysis
│       └── doc_tools.py           # PDF parsing + RAG
├── tests/
│   ├── test_detectives.py
│   ├── test_judges.py
│   └── test_synthesis.py
├── audits/
│   ├── report_onself_generated/   #  my agent vs my repo
│   ├── report_onpeer_generated/    # my agent vs peer repo
│   └── report_bypeer_received/     # Peer agent vs my repo
├── .env.example                    # API key template
├── pyproject.toml                  # uv dependencies
├── README.md                       # This file
└── Dockerfile                      # Optional container
```
## 🚀 Quick Start

### Prerequisites
```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Python 3.10+
python --version
```
# Installation
```bash
# Clone repository
git clone https://github.com/TsegayIS122123/automaton-auditor.git
cd automaton-auditor

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```