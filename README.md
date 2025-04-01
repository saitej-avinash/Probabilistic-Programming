# Probabilistic Programming

This repository explores the intersection of **symbolic execution** and **probabilistic programming**, providing tools and examples to compute probabilities over program paths, simulate randomized algorithms, and analyze program behavior with uncertain inputs.

## Project Overview

The project takes a **random input program**, converts it into **symbolic execution** in a simplified `pWhile` syntax, and calculates **branch probabilities** using probabilistic analysis.

Later, these **branch probabilities** are tested using the **PRISM model checker** by taking the relevant properties from each example and verifying them for correctness and behavior under uncertainty.

## Project Structure

```
Probabilistic-Programming/
│
├── conditionals/
│   ├── parseconditional.py
│   └── parseconditional_fix2.py
│
├── examples/
│   ├── Freivalds.py
│   ├── Random_sample.py
│   ├── example.py
│   └── montyc.py
│
├── pathbranch/
│   ├── branchprob.py
│   ├── pathprob.py
│   └── findpctl.txt
│
└── README.md
```

---

## Modules Overview

### 🔸 `conditionals/`

Tools to parse and analyze conditional branches in code:

- `parseconditional.py`: Parses conditional expressions for probabilistic evaluation.
- `parseconditional_fix2.py`: A refined version with bug fixes or enhancements.

### 🔸 `examples/`

Illustrative scripts demonstrating use cases and concepts:

- `Freivalds.py`: Implements Freivalds' algorithm to probabilistically verify matrix multiplication.
- `Random_sample.py`: Example demonstrating random sampling.
- `example.py`: General-purpose example.
- `montyc.py`: Simulates the Monty Hall problem for probabilistic reasoning.

### 🔸 `pathbranch/`

Core logic for computing probabilities of branching paths:

- `branchprob.py`: Computes probabilities across program branches.
- `pathprob.py`: Symbolic execution with probabilistic estimates.

---

## Getting Started

### Prerequisites

- Python 3.7 or later

### Run an Example

```bash
python examples/montyc.py
```

---

## Use Cases

- **Static Analysis with Uncertainty**: Evaluate how uncertain inputs affect program behavior.
- **Probabilistic Verification**: Estimate correctness probabilities for randomized algorithms.
- **Symbolic Branch Evaluation**: Combine symbolic execution with probabilistic branch conditions.
- **Formal Verification**: Use PRISM model checker to verify program behavior under uncertainty.

---
