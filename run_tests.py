#!/usr/bin/env python3
"""
Test runner for Darwin Agent primitive validation

This script runs all primitive tests and provides a summary report.
"""

import subprocess
import sys
from pathlib import Path

def run_primitive_tests():
    """Run primitive validation tests"""
    project_root = Path(__file__).parent
    test_file = project_root / "tests" / "test_primitives.py"
    
    print("🧪 Darwin Agent - Primitive Validation Test Suite")
    print("=" * 55)
    
    if not test_file.exists():
        print("❌ Test file not found:", test_file)
        return 1
    
    # Run pytest with detailed output
    cmd = [
        sys.executable, "-m", "pytest", 
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print("\n" + "=" * 55)
        if result.returncode == 0:
            print("✅ All primitive validation tests passed!")
        else:
            print("❌ Some tests failed. Check output above.")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_primitive_tests())