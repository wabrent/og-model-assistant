#!/usr/bin/env python3
"""
Script to run OpenGradient SDK integration tests.
Useful for CI/CD pipelines and local testing.
"""
import subprocess
import sys
import os

def run_tests():
    """Run OpenGradient SDK tests."""
    print("🚀 Running OpenGradient SDK Integration Tests")
    print("=" * 60)
    
    # Run pytest with specific test file
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_opengradient_sdk.py",
        "-v",
        "--tb=short"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    print("=" * 60)
    print(f"Exit code: {result.returncode}")
    
    # Summary
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return result.returncode

def run_specific_test(class_name=None, test_name=None):
    """Run specific test class or test."""
    cmd = [sys.executable, "-m", "pytest", "tests/test_opengradient_sdk.py", "-v"]
    
    if class_name and test_name:
        cmd.append(f"::Test{class_name}::test_{test_name}")
    elif class_name:
        cmd.append(f"::Test{class_name}")
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run OpenGradient SDK tests")
    parser.add_argument("--class", dest="test_class", help="Test class to run")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--all", action="store_true", help="Run all SDK tests (default)")
    
    args = parser.parse_args()
    
    if args.test_class or args.test:
        return run_specific_test(args.test_class, args.test).returncode
    else:
        return run_tests()

if __name__ == "__main__":
    sys.exit(main())