# Lab 09 — Deutsch and Deutsch-Jozsa Algorithms

**Topic 5:** Quantum Algorithms  
**Maps to:** LO6 — Establish guidelines for selecting quantum computing algorithms

Implement the first algorithms to show a provable quantum advantage: decide whether a black-box function is constant or balanced with a single query, then generalise from one input bit to n.

## What you'll build

Deutsch and Deutsch-Jozsa circuits with all four oracle types, run on IBM Quantum hardware, correctly classifying each function in one query.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, OpenQASM

## Files

- `deutsch-jozsa.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `deutsch.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main-deutsch-jozsa.py` — Python implementation
- `main.py` — Python implementation

## Run

```bash
python labs/lab09/main.py
```

## Test it

The Deutsch circuit measures 0 for both constant oracles and 1 for both balanced oracles; Deutsch-Jozsa returns the all-zeros string for a constant function and a non-zero string for a balanced function — each using exactly one oracle query.

---

Full step-by-step instructions: **Learner Guide — Activity 9**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
