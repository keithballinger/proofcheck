#!/bin/bash

# Quick ProofCheck Demo - Non-interactive version
# Run all examples without pausing

set -e

echo "Running ProofCheck Quick Demo..."
echo "================================"
echo ""

# Detect how to run proofcheck
if command -v proofcheck &> /dev/null; then
    PROOFCHECK_CMD="proofcheck"
    echo "Using installed proofcheck command"
elif [ -f "proofcheck/src/cli.py" ]; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python not found"
        exit 1
    fi
    PROOFCHECK_CMD="$PYTHON_CMD -m proofcheck.src.cli"
    echo "Running ProofCheck as Python module"
else
    echo "Error: ProofCheck not found!"
    echo "Please install ProofCheck or run from project root"
    exit 1
fi

echo ""

# Translate LaTeX files
echo "1. Translating LaTeX to Lean..."
$PROOFCHECK_CMD translate examples/basic_number_theory.tex
echo ""

# Create a project
echo "2. Creating new Lean project..."
rm -rf demo_project 2>/dev/null || true
$PROOFCHECK_CMD new demo_project
echo ""

# Search Mathlib
echo "3. Searching Mathlib..."
$PROOFCHECK_CMD search "Nat.add"
echo ""

# Show cache stats
echo "4. Cache statistics..."
$PROOFCHECK_CMD cache stats
echo ""

echo "Demo complete! Files created:"
echo "  - examples/basic_number_theory.lean"
echo "  - demo_project/"
echo ""
echo "To clean up: rm -rf demo_project examples/*.lean"