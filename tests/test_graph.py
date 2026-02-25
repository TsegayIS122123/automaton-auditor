""" tests for graph structure"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_graph_nodes_exist():
    """Check that graph.py defines required nodes"""
    with open("src/graph.py", "r") as f:
        content = f.read()
    
    required = ["repo_investigator", "doc_analyst", "evidence_aggregator"]
    for node in required:
        assert node in content, f"Missing {node}"
    print("✅ Graph has all required nodes")
    return True

def test_graph_has_parallel():
    """Check for parallel structure indicators - FIXED VERSION"""
    with open("src/graph.py", "r") as f:
        content = f.read()
    
    # Check for fan-out (multiple edges from START)
    has_fan_out = "add_edge(START, \"repo_investigator\")" in content and \
                  "add_edge(START, \"doc_analyst\")" in content
    assert has_fan_out, "Missing fan-out pattern"
    print("  ✓ Has fan-out from START")
    
    # Check for fan-in (both detectives connect to aggregator)
    has_fan_in = "add_edge(\"repo_investigator\", \"evidence_aggregator\")" in content and \
                 "add_edge(\"doc_analyst\", \"evidence_aggregator\")" in content
    assert has_fan_in, "Missing fan-in pattern"
    print("  ✓ Has fan-in to evidence_aggregator")
    
    print("✅ Graph has parallel structure")
    return True

if __name__ == "__main__":
    print("Testing graph module...")
    tests = [test_graph_nodes_exist, test_graph_has_parallel]
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
    
    print(f"✅ {passed}/{len(tests)} tests passed")