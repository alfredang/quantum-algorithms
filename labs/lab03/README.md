# Lab 03 — Superposition and Entanglement on IBM Quantum

**Topic 2:** Introduction to Quantum Computing Systems  
**Maps to:** LO2, LO4 — Evaluate quantum computing applicability in the business context

Create your IBM Quantum account, build a superposition circuit and a two-qubit Bell state, and run them on a real quantum processor to see genuine quantum randomness and correlation in the results.

## What you'll build

A Bell state circuit executed on real IBM Quantum hardware, with a measured histogram showing the |00> and |11> correlation.

**Tools:** IBM Quantum Platform, Qiskit Runtime, Python 3.13

## Files

- `main.py` — Python implementation

## Run

```bash
python labs/lab03/main.py
```

## Test it

The superposition circuit gives roughly 50% |0> and 50% |1>; the Bell circuit gives roughly 50% |00> and 50% |11> with only a small percentage of |01> and |10> counts caused by hardware noise.

---

Full step-by-step instructions: **Learner Guide — Activity 3**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
