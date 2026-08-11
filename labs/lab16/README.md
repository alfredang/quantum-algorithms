# Lab 16 — Portfolio Optimisation with QAOA (Finance)

**Topic 7:** Quantum Computing Applications and Use Cases  
**Maps to:** LO4, LO6 — Evaluate applicability and select appropriate algorithms

Apply the Quantum Approximate Optimization Algorithm to a Max-Cut style combinatorial problem, the same structure that underlies portfolio selection, routing and scheduling in financial services.

## What you'll build

A QAOA run that finds the optimal cut on a small graph, with the solution quality compared against brute force.

**Tools:** Qiskit 2.x, NetworkX, SciPy, matplotlib

## Files

- `main.py` — Python implementation
- `qaoa-maxcut.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab16/main.py
```

## Test it

The most frequently sampled bit string from the optimised QAOA circuit corresponds to the true maximum cut found by brute force, and the approximation ratio improves as the number of layers p increases.

---

Full step-by-step instructions: **Learner Guide — Activity 16**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
