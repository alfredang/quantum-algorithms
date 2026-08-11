# Lab 06 — Quantum Teleportation

**Topic 4:** Quantum Protocols  
**Maps to:** LO3, LO7 — Synthesize quantum methodologies to address complex problems

Implement the three-qubit teleportation protocol: entangle a shared pair, perform a Bell measurement on the unknown state, and apply the conditional corrections that recreate the original state on Bob's qubit.

## What you'll build

A teleportation circuit run on IBM Quantum hardware that reconstructs an arbitrary input state at the receiving qubit.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, OpenQASM

## Files

- `main.py` — Python implementation
- `teleportation-alt.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `teleportation.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab06/main.py
```

## Test it

The measurement statistics on Bob's qubit q2 match the amplitudes of the state originally prepared on q0, within hardware noise, and the original state no longer exists on q0.

---

Full step-by-step instructions: **Learner Guide — Activity 6**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
