# Lab 17 — Bit-Flip and Phase-Flip Error Correction Codes

**Topic 8:** Quantum Error Correction  
**Maps to:** LO7 — Synthesize quantum methodologies to address complex problems

Build the three-qubit repetition codes that detect and correct X and Z errors: encode a logical qubit, inject an error, measure the syndrome without collapsing the state, and apply the correction.

## What you'll build

Working bit-flip and phase-flip code circuits that correctly identify and repair an injected single-qubit error.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, OpenQASM

## Files

- `bit-flip-code.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main-phase-flip.py` — Python implementation
- `main.py` — Python implementation
- `phase-flip-code.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab17/main.py
```

## Test it

The syndrome measurement correctly identifies which qubit carried the injected error without collapsing the logical state, and applying the indicated correction restores the original logical qubit.

---

Full step-by-step instructions: **Learner Guide — Activity 17**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
