# Lab 05 — Quantum Gates and Bell/GHZ States with PennyLane

**Topic 3:** Quantum Gates and Circuits  
**Maps to:** LO3, LO5 — Direct two-level quantum models and apply quantum gates

Use PennyLane's quantum-function and QNode model to apply the full single- and multi-qubit gate set, then construct Bell and GHZ entangled states and verify their measurement correlations.

## What you'll build

A PennyLane script that draws each circuit, returns the state vector, and confirms the Bell and GHZ correlations.

**Tools:** PennyLane, Python 3.13, matplotlib

## Files

- `main.py` — Python implementation

## Run

```bash
python labs/lab05/main.py
```

## Test it

The Bell state returns amplitudes of about 0.707 on |00> and |11> and zero elsewhere; the GHZ state returns amplitudes only on |000> and |111>; the phase-kickback circuit shows the eigenvalue phase transferred to the control qubit.

---

Full step-by-step instructions: **Learner Guide — Activity 5**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
