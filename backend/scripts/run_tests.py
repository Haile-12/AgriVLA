#!/usr/bin/env python
"""
Convenience script to run unit and integration tests.

Usage:
  python scripts/run_tests.py
"""
import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=".."
    )
    sys.exit(result.returncode)
