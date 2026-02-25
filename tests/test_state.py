""" tests for state models"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that state module imports correctly"""
    try:
        from src.state import Evidence, JudicialOpinion, AgentState
        print("✅ State imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_evidence_creation():
    """Test creating an Evidence object"""
    from src.state import Evidence
    from datetime import datetime
    
    ev = Evidence(
        goal="Test goal",
        found=True,
        location="test.py",
        rationale="test",
        confidence=0.9,
        collected_by="RepoInvestigator"
    )
    assert ev.goal == "Test goal"
    assert ev.found is True
    print("✅ Evidence creation works")
    return True

if __name__ == "__main__":
    print("Testing state module...")
    tests = [test_imports, test_evidence_creation]
    passed = sum(1 for t in tests if t())
    print(f"✅ {passed}/{len(tests)} tests passed")