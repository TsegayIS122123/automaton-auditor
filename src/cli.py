#!/usr/bin/env python
"""Command-line interface for Automaton Auditor"""

import argparse
import sys
from pathlib import Path

from .graph import run_detective_phase

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Automaton Auditor - Autonomous Code Audit System"
    )
    
    parser.add_argument(
        "repo_url",
        help="GitHub repository URL to audit (e.g., https://github.com/user/repo)"
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to PDF report file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed evidence"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON format)"
    )
    
    args = parser.parse_args()
    
    print(f"\n🔍 Automaton Auditor - Analyzing {args.repo_url}")
    print(f"📄 Using report: {args.pdf_path}")
    print("-" * 50)
    
    # Run the graph
    result = run_detective_phase(args.repo_url, args.pdf_path)
    
    # Print summary
    total_evidence = sum(len(e) for e in result["evidences"].values())
    print(f"\n📊 Collected {total_evidence} evidence items")
    
    if args.verbose:
        for source, evidences in result["evidences"].items():
            print(f"\n🔍 {source.upper()}:")
            for ev in evidences:
                status = "✅" if ev.found else "❌"
                print(f"  {status} {ev.goal[:50]}...")
    
    # Save output if requested
    if args.output:
        import json
        from datetime import datetime
        
        # Convert evidence to serializable format
        output_data = {
            "repo_url": args.repo_url,
            "timestamp": datetime.now().isoformat(),
            "total_evidence": total_evidence,
            "evidence_summary": {
                source: len(ev_list) 
                for source, ev_list in result["evidences"].items()
            }
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())