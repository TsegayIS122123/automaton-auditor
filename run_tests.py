#!/usr/bin/env python
""" test runner"""

import subprocess
import sys

tests = [
    "tests/test_state.py",
    "tests/test_tools.py",
    "tests/test_graph.py"
]

print("=" * 50)
print("🧪 RUNNING MINIMAL TESTS")
print("=" * 50)

passed = 0
for test in tests:
    print(f"\n📋 Running {test}...")
    result = subprocess.run([sys.executable, test])
    if result.returncode == 0:
        passed += 1
        print(f"✅ {test} PASSED")
    else:
        print(f"❌ {test} FAILED")

print("\n" + "=" * 50)
print(f"📊 SUMMARY: {passed}/{len(tests)} test suites passed")
print("=" * 50)