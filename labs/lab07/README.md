# Lab 07 — Superdense Coding Protocol

**Topic 4:** Quantum Protocols  
**Maps to:** LO3, LO7 — Direct two-level quantum models for quantum computing

Implement the dual of teleportation: transmit two classical bits by sending only a single qubit of a pre-shared entangled pair, encoding the message with the I, X, Z and XZ operations.

## What you'll build

A superdense coding circuit that correctly transmits all four two-bit messages 00, 01, 10 and 11.

**Tools:** Qiskit 2.x, IBM Quantum Runtime

## Files

- `main.py` — Python implementation
- `superdense-coding.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab07/main.py
```

## Test it

Each of the four encodings decodes to its intended message — identity gives 00, X gives 01, Z gives 10 and ZX gives 11 — demonstrating two classical bits carried by one transmitted qubit.

---

Full step-by-step instructions: **Learner Guide — Activity 7**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
