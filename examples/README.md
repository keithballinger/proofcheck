# ProofCheck Examples

This directory contains example Lean projects and LaTeX files to help you get started with ProofCheck.

## Quick Start

We provide two demo scripts to show ProofCheck in action:

### Interactive Demo (Recommended)
```bash
./examples/run_examples.sh
```
This walks you through each feature step-by-step with explanations.

### Quick Demo
```bash
./examples/quick_demo.sh
```
This runs all examples quickly without pausing.

## Examples

### 1. Basic Number Theory (`basic_number_theory.tex`)
A simple LaTeX file demonstrating basic number theory theorems that can be translated to Lean.

### 2. Prime Numbers (`prime_numbers.tex`)
Example proofs about prime numbers in LaTeX format.

### 3. Set Theory (`set_theory.tex`)
Basic set theory definitions and theorems.

## Usage

### Translating LaTeX to Lean

To translate any of these LaTeX examples to Lean:

```bash
proofcheck translate examples/basic_number_theory.tex
```

This will create a corresponding `.lean` file with the translated content.

### Creating a New Lean Project

To create a new Lean project for your proofs:

```bash
proofcheck new my_proofs
cd my_proofs
```

### Checking Your Proofs

To verify your proofs (this automatically builds the project):

```bash
proofcheck check MyProof.lean
```

The `check` command will:
1. Find the project root
2. Run `lake build` to compile the project
3. Report any errors or confirm successful verification

### Searching Mathlib

To find relevant theorems and definitions:

```bash
proofcheck search "prime number"
proofcheck search "Nat.add"
```

## Tips

1. The translator provides a starting point - you'll usually need to adjust the output
2. Use `proofcheck search` to find the correct Mathlib theorems
3. Start with simple proofs and gradually work up to more complex ones
4. The Lean 4 documentation is your friend: https://leanprover.github.io/lean4/doc/