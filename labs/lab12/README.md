# Lab 12 — Quantum Fourier Transform

**Topic 5:** Quantum Algorithms  
**Maps to:** LO6, LO7 — Establish guidelines for selecting quantum computing algorithms

Build the QFT circuit from Hadamard and controlled-phase gates, verify it against the classical DFT, and understand why it is the engine behind phase estimation and Shor's algorithm.

## What you'll build

QFT circuits for 3, 4 and 5 qubits, validated against a classical DFT reference and run on IBM Quantum hardware.

**Tools:** Qiskit 2.x, NumPy, IBM Quantum Runtime, OpenQASM

## Files

- `main.py` — Python implementation
- `qft-3qubit.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `qft-4qubit.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `qft-5qubit.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab12/main.py
```

## Test it

Your hand-built QFT circuit produces the same state vector as Qiskit's built-in QFT and matches a normalised classical FFT of the same input, using on the order of n^2 gates.

---

Full step-by-step instructions: **Learner Guide — Activity 12**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
