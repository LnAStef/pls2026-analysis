#!/usr/bin/env python3
"""Mutation experiment for deconvolve.py.

Copies src/spatial_decode and tests/test_deconvolve.py into a temporary folder,
applies each mutation to the COPY, runs pytest on the copy, and prints a table.
Nothing in your repository is modified.

Usage (from the project root, with your environment active):
    1. Fill in PREDICTIONS below ("caught" or "survives") BEFORE running.
    2. python run_mutations_deconvolve.py
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "src" / "spatial_decode"
TARGET = "deconvolve.py"
TESTS = ROOT / "tests"
TEST_FILE = "test_deconvolve.py"

# Write your prediction for each mutation BEFORE you run the script.
PREDICTIONS = {1: "CAUGHT", 2: "CAUGHT", 3: "CAUGHT", 4: "CAUGHT", 5: "SURVIVED", 6: "SURVIVED"}

# (number, description, exact text to find (must occur once), replacement)
MUTATIONS = [
    (1, "normalise_columns returns S unchanged",
     "return S / S.sum()", "return S"),
    (2, "genes matched by position, not name",
     "counts = binned_counts.loc[:, S.index]", "counts = binned_counts"),
    (3, "no ValueError on mismatched genes",
     '    if set(S.index) != set(binned_counts.columns):\n'
     '        raise ValueError("gene names of S and binned_counts do not match")\n',
     ""),
    (4, "to_fractions returns raw weights",
     "return weights / total", "return weights"),
    (5, "to_fractions without the zero-total guard",
     "    if total == 0:\n        return np.full(weights.shape, np.nan)\n", ""),
    (6, "rows normalised instead of columns",
     "return S / S.sum()", "return S.div(S.sum(axis=1), axis=0)"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_env(work):
    old = os.environ.get("PYTHONPATH", "")
    path = os.pathsep.join(p for p in [str(work / "src"), old] if p)
    return {**os.environ, "PYTHONPATH": path, "PYTHONDONTWRITEBYTECODE": "1"}


def run_pytest(work):
    """Return (exit code, names of failed tests, last summary line)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/{TEST_FILE}", "-q", "--tb=no",
         "-rf", "-p", "no:cacheprovider"],
        cwd=work, env=make_env(work), capture_output=True, text=True, timeout=300,
    )
    failed = re.findall(r"^FAILED \S+::(\w+)", r.stdout, re.M)
    lines = r.stdout.strip().splitlines()
    summary = lines[-1] if lines else r.stderr.strip()[-200:]
    return r.returncode, failed, summary


def imported_from(work):
    r = subprocess.run(
        [sys.executable, "-c",
         "import spatial_decode.deconvolve as m; print(m.__file__)"],
        cwd=work, env=make_env(work), capture_output=True, text=True,
    )
    return Path(r.stdout.strip()).resolve() if r.stdout.strip() else None


def main():
    target_real = PKG / TARGET
    before = sha(target_real)

    with tempfile.TemporaryDirectory(prefix="mutation_") as tmp:
        work = Path(tmp)
        shutil.copytree(PKG, work / "src" / "spatial_decode",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (work / "tests").mkdir()
        shutil.copy(TESTS / TEST_FILE, work / "tests" / TEST_FILE)
        if (TESTS / "conftest.py").exists():
            shutil.copy(TESTS / "conftest.py", work / "tests" / "conftest.py")

        # Make sure pytest really imports the COPY, not your installed package.
        where = imported_from(work)
        if where is None or work.resolve() not in where.parents:
            sys.exit(f"ABORT: tests would import {where}, not the temporary copy.")

        # The tests must pass on the unmutated code, otherwise results mean nothing.
        code, failed, summary = run_pytest(work)
        print(f"baseline (unmutated): {summary}")
        if code != 0:
            sys.exit(f"ABORT: baseline is not green: {failed or summary}")

        target = work / "src" / "spatial_decode" / TARGET
        original = target.read_text()
        rows = []
        for number, description, old, new in MUTATIONS:
            count = original.count(old)
            if count != 1:
                rows.append((number, description, "NOT APPLIED",
                             f"pattern found {count} times, expected 1"))
                print(f"  {number}: not applied ({count} matches)")
                continue
            target.write_text(original.replace(old, new, 1))
            code, failed, summary = run_pytest(work)
            if code == 1 and failed:
                result = "CAUGHT"
            elif code == 0:
                result = "SURVIVED"
            else:
                result = "ERROR (code did not run; not a real catch)"
            rows.append((number, description, result, ", ".join(failed) or summary))
            print(f"  {number}: {result}")
            target.write_text(original)

    print("\n| # | Mutation | Predicted | Result | Tests that failed |")
    print("|---|---|---|---|---|")
    surprises, survivors = [], []
    for number, description, result, detail in rows:
        predicted = PREDICTIONS.get(number, "").strip().lower()
        flag = ""
        if predicted:
            actual = "survives" if result == "SURVIVED" else "caught"
            if predicted != actual:
                flag = " (surprise)"
                surprises.append(number)
        if result == "SURVIVED":
            survivors.append(number)
        print(f"| {number} | {description} | {predicted or '-'} | {result}{flag} | {detail} |")

    print(f"\nsurvivors: {survivors or 'none'}")
    if surprises:
        print(f"predictions that were wrong: {surprises}")
    after = sha(target_real)
    print(f"your {TARGET} unchanged: {before == after}")


if __name__ == "__main__":
    main()
