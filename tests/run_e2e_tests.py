#!/usr/bin/env python3
"""
Comprehensive end-to-end test runner.
Runs: old notebook logic tests, new expansion tests, and notebook execution (optional).
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run_pytest():
    """Run pytest on tests/."""
    try:
        import pytest
    except ImportError:
        print("pytest not installed. Install with: pip install pytest")
        return False
    return pytest.main(["-v", str(ROOT / "tests"), "--tb=short"]) == 0


def run_notebook_execution():
    """Execute original notebooks with nbconvert (optional; requires CSV + optional IEX)."""
    try:
        import nbconvert
        from nbconvert.preprocessors import ExecutePreprocessor
        import nbformat
    except ImportError:
        print("nbconvert not installed. Skipping notebook execution.")
        return None  # skip, not fail
    fixtures = ROOT / "tests" / "fixtures" / "constituents_fixture.csv"
    results = {}
    for name in ["001_equal_weight_S&P_500.ipynb", "002_quantitative_momentum_strategy.ipynb", "003_quantitative_value_strategy.ipynb"]:
        nb_path = ROOT / "finished_files" / name
        if not nb_path.exists():
            results[name] = "skip (not found)"
            continue
        # Copy fixture to finished_files so notebook finds sp_500_stocks.csv
        if fixtures.exists():
            import shutil
            dest = ROOT / "finished_files" / "sp_500_stocks.csv"
            shutil.copy(fixtures, dest)
        # Create a minimal secrets stub if missing
        secrets_py = ROOT / "finished_files" / "secrets.py"
        if not secrets_py.exists():
            secrets_py.write_text('IEX_CLOUD_API_TOKEN = "pk_test_placeholder"\n')
            cleanup_secrets = True
        else:
            cleanup_secrets = False
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=120)
            ep.preprocess(nb, {"metadata": {"path": str(ROOT / "finished_files")}})
            results[name] = "OK"
        except Exception as e:
            results[name] = str(e)[:80]
        finally:
            if cleanup_secrets and secrets_py.exists():
                try:
                    secrets_py.unlink()
                except Exception:
                    pass
    for name, status in results.items():
        print(f"  {name}: {status}")
    return all(v == "OK" for v in results.values())


def main():
    print("=== E2E Tests: Old notebook logic + New expansion ===\n")
    # 1) Pytest
    print("1) Running pytest (old logic + new expansion)...")
    ok = run_pytest()
    print("   Result:", "PASS" if ok else "FAIL")
    # 2) Optional notebook execution
    print("\n2) Optional: Execute original notebooks...")
    nb_ok = run_notebook_execution()
    if nb_ok is not None:
        print("   Result:", "PASS" if nb_ok else "FAIL (or skip)")
    # 3) Scripts
    print("\n3) Running scripts (exit codes)...")
    scripts = [
        ("rebalance.py", ["--out", str(ROOT / "output" / "rebalance_trades.csv")]),
        ("compare_etfs.py", []),
        ("run_backtest.py", []),
        ("run_all_expansions.py", []),
    ]
    for script, args in scripts:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)] + args,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        status = "OK" if r.returncode == 0 else f"exit {r.returncode}"
        if r.returncode != 0 and r.stderr:
            status += " " + r.stderr[:60].replace("\n", " ")
        print(f"   {script}: {status}")
    print("\n=== Done ===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
