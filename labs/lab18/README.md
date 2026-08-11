# Lab 18 — Shor 9-Qubit and Steane 7-Qubit Codes

**Topic 8:** Quantum Error Correction  
**Maps to:** LO7 — Synthesize quantum methodologies to address complex problems

Step up to codes that correct arbitrary single-qubit errors: Shor's 9-qubit concatenated code and Steane's more efficient 7-qubit CSS code, then compare their qubit overhead and discuss the road to fault tolerance.

## What you'll build

Working Shor 9-qubit and Steane 7-qubit code circuits, with a comparison of qubit cost against protection offered.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, OpenQASM

## Files

- `main-steane.py` — Python implementation
- `main.py` — Python implementation
- `shor-9qubit-code.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `steane-7qubit-code.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab18/main.py
```

## Test it

Both the Shor 9-qubit and Steane 7-qubit circuits detect and correct an arbitrary injected single-qubit error (X, Y or Z), and you can state the qubit overhead each code requires.

---

Full step-by-step instructions: **Learner Guide — Activity 18**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
