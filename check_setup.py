"""Pre-flight check. Run this before the Week 2 session:  python check_setup.py

It does not fix anything. It tells you what is missing, so that the session is not spent
on installation.

`ruff` is reported as a warning rather than a failure: it is in `environment.yml` and you will
need it from Week 5, so a warning here means your environment was not built from that file.
"""
import pathlib
import re
import shutil
import subprocess
import sys

# Importable packages. The command-line tools (git, conda, jupyter, ruff) are checked below.
REQUIRED = ["numpy", "scipy", "pandas", "matplotlib", "sklearn", "yaml", "pytest"]


def version_of(cmd):
    exe = shutil.which(cmd)
    if exe is None:
        return None
    try:
        out = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=15)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception:
        return "found, but would not report a version"


def main():
    problems = []

    py = sys.version_info
    ok = (py.major, py.minor) >= (3, 11)
    print(f"[{'PASS' if ok else 'FAIL'}] Python {py.major}.{py.minor}.{py.micro} (need 3.11+)")
    if not ok:
        problems.append("Python is older than 3.11")

    for cmd, needed in (("git", True), ("conda", True), ("jupyter", True), ("ruff", False)):
        v = version_of(cmd)
        if v:
            print(f"[PASS] {cmd}: {v}")
        else:
            print(f"[{'FAIL' if needed else 'WARN'}] {cmd} not found on PATH")
            if needed:
                problems.append(f"{cmd} is not installed or not on PATH")

    for mod in REQUIRED:
        try:
            __import__(mod)
            print(f"[PASS] import {mod}")
        except ImportError:
            print(f"[FAIL] cannot import {mod}")
            problems.append(f"package missing: {mod}")

    # Your own package, installed editable. Until `pip install -e .` has been run, your code is
    # importable only from this directory, and your tests will not find it from anywhere else.
    # Read the name with a regex rather than tomllib: this script has to survive being run on
    # the wrong Python, and tomllib only exists from 3.11.
    name = None
    try:
        m = re.search(r'^name\s*=\s*"([^"]+)"', pathlib.Path("pyproject.toml").read_text(), re.M)
        name = m.group(1) if m else None
    except OSError:
        print("[WARN] no pyproject.toml here — are you in the project root?")
    if name in (None, "REPLACE-ME"):
        if name == "REPLACE-ME":
            print("[WARN] pyproject.toml: name is still REPLACE-ME — set it to your package")
    else:
        module = name.replace("-", "_")
        try:
            __import__(module)
            print(f"[PASS] import {module} (your package, installed)")
        except ImportError:
            # Two different situations, and telling them apart saves an afternoon: the package
            # directory may not exist yet (expected until Week 3), or it exists and the install
            # has not been run.
            if not pathlib.Path("src", module).is_dir():
                print(f"[WARN] no src/{module}/ yet — expected until Week 3, when you create it")
            else:
                print(f"[FAIL] cannot import {module} — run  pip install -e .")
                problems.append("your own package is not installed: run  pip install -e .")

    print()
    if problems:
        print("NOT READY. Fix these before the session:")
        for p in problems:
            print(f"  - {p}")
        print("\nMost of them are fixed by:  conda env create -f environment.yml")
        print("and, for your own package:      pip install -e .")
        sys.exit(1)
    print("READY. Bring your laptop and your questions.")


if __name__ == "__main__":
    main()
