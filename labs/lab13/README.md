# Lab 13 — Shor's Algorithm and the Quantum Threat to RSA

**Topic 6:** Quantum Cryptography and Quantum Safety  
**Maps to:** LO7 — Synthesize quantum methodologies to address complex problems

See how factoring reduces to period finding, run the quantum period-finding circuit that sits at the heart of Shor's algorithm, and recover the factors of N = 15 from the measured period.

## What you'll build

A period-finding circuit whose measured output yields the period r, from which the factors of N = 15 are classically recovered.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, Python, OpenQASM

## Files

- `main.py` — Python implementation
- `shor-period-finding.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab13/main.py
```

## Test it

The measured phase yields period r = 4 for a = 7 and N = 15, and the classical post-processing step recovers the correct factors 3 and 5.

---

Full step-by-step instructions: **Learner Guide — Activity 13**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
