#!/bin/bash
# scripts/reproduce_small.sh - Runs 50-sample reproduction pipeline end-to-end.
set -e

echo "Running small reproduction test (N=50 questions)..."

if [ -f "./venv/Scripts/python.exe" ]; then
    ./venv/Scripts/python.exe scripts/reproduce_small.py
elif [ -f "./venv/bin/python" ]; then
    ./venv/bin/python scripts/reproduce_small.py
else
    python scripts/reproduce_small.py
fi
