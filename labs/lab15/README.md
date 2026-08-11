# Lab 15 — Molecular Simulation with VQE (Healthcare & Science)

**Topic 7:** Quantum Computing Applications and Use Cases  
**Maps to:** LO4, LO7 — Evaluate quantum computing applicability in the business context

Run the Variational Quantum Eigensolver to compute the ground-state energy of the hydrogen molecule — the flagship near-term use case for drug discovery, catalysis and materials science.

## What you'll build

A VQE run that converges to the H2 ground-state energy, with an energy-versus-iteration convergence plot.

**Tools:** Qiskit 2.x, SciPy optimiser, matplotlib, IBM Quantum

## Files

- `main.py` — Python implementation
- `vqe-h2.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer

## Run

```bash
python labs/lab15/main.py
```

## Test it

The VQE optimisation converges to an energy close to the exact H2 ground-state value of about -1.137 Hartree, and the convergence plot shows the energy decreasing monotonically toward that limit.

---

Full step-by-step instructions: **Learner Guide — Activity 15**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
