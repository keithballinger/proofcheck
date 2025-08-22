# ProofCheck Examples

This directory contains example Lean projects and LaTeX files to help you get started with ProofCheck.

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
lake build
```

### Checking Your Proofs

After writing or translating your proofs:

```bash
proofcheck check MyProof.lean
```

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