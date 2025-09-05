#!/usr/bin/env python3
"""
Test runner script for the finreview project
"""
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests with coverage"""
    project_root = Path(__file__).parent
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=pdf_processor",
        "--cov=sql_utils", 
        "--cov=api",
        "--cov=operations_matcher",
        "--cov=rules_manager",
        "--cov=rules_models",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80"
    ]
    
    print("Running tests with coverage...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


def run_unit_tests():
    """Run only unit tests"""
    project_root = Path(__file__).parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "unit",
        "-v"
    ]
    
    print("Running unit tests...")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ Unit tests passed!")
    else:
        print("\n❌ Unit tests failed!")
        sys.exit(1)


def run_integration_tests():
    """Run only integration tests"""
    project_root = Path(__file__).parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "integration",
        "-v"
    ]
    
    print("Running integration tests...")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ Integration tests passed!")
    else:
        print("\n❌ Integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            run_unit_tests()
        elif sys.argv[1] == "integration":
            run_integration_tests()
        else:
            print("Usage: python run_tests.py [unit|integration]")
            sys.exit(1)
    else:
        run_tests()
