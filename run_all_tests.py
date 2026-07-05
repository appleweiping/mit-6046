"""Run every problem set's test suite and print a summary.

Usage:
    D:\\Project\\_csdiy\\.venv-ml\\Scripts\\python.exe run_all_tests.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PS_DIRS = ["ps1", "ps2", "ps4", "ps5", "ps6", "ps7", "ps8", "ps9", "ps10"]


def main():
    py = sys.executable
    all_ok = True
    for ps in PS_DIRS:
        d = os.path.join(ROOT, "code", ps)
        if not os.path.isdir(d):
            continue
        proc = subprocess.run(
            [py, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            cwd=d, capture_output=True, text=True)
        last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
        status = "OK " if proc.returncode == 0 else "FAIL"
        all_ok &= (proc.returncode == 0)
        print(f"[{status}] {ps:5s}  {last}")
    print("\nALL TESTS PASSED" if all_ok else "\nSOME TESTS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
