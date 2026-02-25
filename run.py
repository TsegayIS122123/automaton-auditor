#!/usr/bin/env python
"""
Explicit run command for Automaton Auditor

Usage:
    python run.py https://github.com/user/repo reports/report.pdf
"""

import sys
from src.graph import run_detective_phase

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python run.py <repo_url> <pdf_path>")
        print("   Example: python run.py https://github.com/langchain-ai/langgraph reports/interim_report.pdf")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    pdf_path = sys.argv[2]
    
    print(f"\n🚀 Automaton Auditor - Detective Phase")
    print(f"📦 Repository: {repo_url}")
    print(f"📄 PDF Report: {pdf_path}")
    print("-" * 50)
    
    result = run_detective_phase(repo_url, pdf_path)
    
    total = sum(len(e) for e in result["evidences"].values())
    print(f"\n✅ Done! Collected {total} evidence items")