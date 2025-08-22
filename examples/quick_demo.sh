#!/bin/bash

# Quick ProofCheck Demo - Non-interactive version
# Run all examples without pausing

set -e

echo "Running ProofCheck Quick Demo..."
echo "================================"
echo ""

# Translate LaTeX files
echo "1. Translating LaTeX to Lean..."
proofcheck translate examples/basic_number_theory.tex
echo ""

# Create a project
echo "2. Creating new Lean project..."
rm -rf demo_project 2>/dev/null || true
proofcheck new demo_project
echo ""

# Search Mathlib
echo "3. Searching Mathlib..."
proofcheck search "Nat.add"
echo ""

# Show cache stats
echo "4. Cache statistics..."
proofcheck cache stats
echo ""

echo "Demo complete! Files created:"
echo "  - examples/basic_number_theory.lean"
echo "  - demo_project/"
echo ""
echo "To clean up: rm -rf demo_project examples/*.lean"