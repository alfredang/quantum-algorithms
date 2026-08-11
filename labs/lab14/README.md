# Lab 14 — Post-Quantum Cryptography Migration Assessment

**Topic 6:** Quantum Cryptography and Quantum Safety  
**Maps to:** LO4, LO7 — Evaluate quantum applicability in the business context

Assess which cryptography in a realistic system is broken by a quantum computer, map each algorithm to its NIST post-quantum replacement, and produce a prioritised migration plan against the harvest-now-decrypt-later risk.

## What you'll build

A completed cryptographic inventory and a prioritised PQC migration plan for a sample organisation.

**Tools:** NIST FIPS 203/204/205, OpenSSL, Python

## Files

- `main.py` — Python implementation

## Run

```bash
python labs/lab14/main.py
```

## Test it

Your inventory correctly separates Shor-broken asymmetric algorithms from Grover-weakened symmetric ones, maps each to the correct NIST FIPS standard, and ranks migration priority by how long the data must remain confidential.

---

Full step-by-step instructions: **Learner Guide — Activity 14**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
