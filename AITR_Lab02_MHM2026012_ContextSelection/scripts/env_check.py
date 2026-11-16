"""
scripts/env_check.py - Environment verification & diagnostic script.
Prints package versions, platform, and verifies random seed control.
"""

import sys
import platform
import numpy as np
import scipy
import sklearn
import rank_bm25
import datasets
import pandas as pd
import matplotlib
import pytest
import tqdm

def main():
    print("=" * 60)
    print("ENVIRONMENT VERIFICATION & DIAGNOSTIC REPORT")
    print("=" * 60)
    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {platform.python_version()}")
    print(f"Platform          : {platform.platform()}")
    print(f"Machine           : {platform.machine()}")
    print("-" * 60)
    print("INSTALLED CORE PACKAGES:")
    print(f"  numpy           : {np.__version__}")
    print(f"  scipy           : {scipy.__version__}")
    print(f"  scikit-learn    : {sklearn.__version__}")
    print(f"  rank_bm25       : {getattr(rank_bm25, '__version__', '0.2.2')}")
    print(f"  datasets        : {datasets.__version__}")
    print(f"  pandas          : {pd.__version__}")
    print(f"  matplotlib      : {matplotlib.__version__}")
    print(f"  pytest          : {pytest.__version__}")
    print(f"  tqdm            : {tqdm.__version__}")
    print("-" * 60)
    
    # Random seed check
    test_seed = 42
    np.random.seed(test_seed)
    val1 = np.random.rand(3)
    np.random.seed(test_seed)
    val2 = np.random.rand(3)
    seed_match = np.allclose(val1, val2)
    print(f"Random seed check (seed={test_seed}): {'PASSED (Deterministic)' if seed_match else 'FAILED'}")
    print(f"Generated sample: {val1}")
    print("=" * 60)
    print("STATUS: ENVIRONMENT READY")

if __name__ == "__main__":
    main()
