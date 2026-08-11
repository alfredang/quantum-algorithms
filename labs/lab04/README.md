# Lab 04 — Building Circuits in IBM Quantum Composer

**Topic 3:** Quantum Gates and Circuits  
**Maps to:** LO5 — Spearhead the application of quantum gates to quantum computing domains

Use the drag-and-drop IBM Quantum Composer to build single- and multi-qubit circuits, watch the state vector and probability panels update live, and export the circuit as OpenQASM.

## What you'll build

A set of Composer circuits (X, H, CNOT, Bell state) with their statevector output, exported as OpenQASM 3 code.

**Tools:** IBM Quantum Composer, OpenQASM 3

## Files

- `bell-state.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main.py` — Python implementation

## Run

```bash
python labs/lab04/main.py
```

## Test it

The Composer probability panel shows a 50/50 split between |00> and |11> for the Bell circuit, and the exported OpenQASM contains an h instruction followed by a cx instruction.

---

Full step-by-step instructions: **Learner Guide — Activity 4**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
