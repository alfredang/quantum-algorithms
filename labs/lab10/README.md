# Lab 10 — Bernstein-Vazirani Algorithm

**Topic 5:** Quantum Algorithms  
**Maps to:** LO6 — Establish guidelines for selecting quantum computing algorithms

Recover an n-bit hidden string in a single oracle query. Classically you would need n queries — one per bit — making this a clean demonstration of linear-to-constant query speedup.

## What you'll build

A Bernstein-Vazirani circuit that recovers a chosen hidden string such as 1011 in one query on real hardware.

**Tools:** Qiskit 2.x, IBM Quantum Runtime

## Files

- `bernstein-vazirani.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main.py` — Python implementation

## Run

```bash
python labs/lab10/main.py
```

## Test it

The most frequent measured bit string equals the hidden string s that was encoded in the oracle, recovered with a single oracle query regardless of the length of s.

---

Full step-by-step instructions: **Learner Guide — Activity 10**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
