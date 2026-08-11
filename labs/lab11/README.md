# Lab 11 — Grover's Search Algorithm

**Topic 5:** Quantum Algorithms  
**Maps to:** LO6, LO7 — Select algorithms and synthesize quantum methodologies

Implement amplitude amplification to find a marked item in an unstructured search space, using the phase oracle and the diffuser, and see the quadratic O(sqrt(N)) speedup for 2-qubit and 3-qubit searches.

## What you'll build

Grover circuits for 2 and 3 qubits that amplify the marked state to a high measurement probability on real hardware.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, OpenQASM

## Files

- `grover-2qubit.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `grover-3qubit.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main.py` — Python implementation

## Run

```bash
python labs/lab11/main.py
```

## Test it

For 2 qubits the marked state is measured with near-certainty after one Grover iteration; for 3 qubits it dominates the histogram after two iterations; applying too many iterations visibly reduces the success probability.

---

Full step-by-step instructions: **Learner Guide — Activity 11**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
