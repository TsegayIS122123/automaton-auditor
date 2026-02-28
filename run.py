#!/usr/bin/env python
"""
Explicit run command for Automaton Auditor

Usage:
    python run.py https://github.com/user/repo reports/report.pdf
"""
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv()
import sys
from src.graph import run_full_audit  # Changed from run_detective_phase

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python run.py <repo_url> <pdf_path>")
        print("   Example: python run.py https://github.com/langchain-ai/langgraph reports/interim_report.pdf")
        sys.exit(1)

    repo_url = sys.argv[1]
    pdf_path = sys.argv[2]

    print(f"\n🚀 Automaton Auditor - Full Audit")
    print(f"📦 Repository: {repo_url}")
    print(f"📄 PDF Report: {pdf_path}")
    print("-" * 50)

    result = run_full_audit(repo_url, pdf_path)  # Changed function call

    # Print summary
    total_evidence = sum(len(e) for e in result["evidences"].values())
    total_opinions = len(result.get("opinions", []))
    has_report = "Yes" if result.get("final_report") else "No"
    
    print(f"\n✅ Audit completed!")
    print(f"📊 Evidence collected: {total_evidence}")
    print(f"⚖️ Opinions generated: {total_opinions}")
    print(f"📄 Final report: {has_report}")