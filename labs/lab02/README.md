# Lab 02 — Visualising a Qubit on the Bloch Sphere

**Topic 2:** Introduction to Quantum Computing Systems  
**Maps to:** LO2 — Decide on appropriate physical methodologies specific to quantum computing problems

Build single-qubit states in Qiskit and plot them on the Bloch sphere, so you can see how gates rotate a qubit and what superposition and phase actually look like geometrically.

## What you'll build

A set of Bloch-sphere plots showing |0>, |1>, |+>, |-> and an arbitrary Ry-rotated state.

**Tools:** Qiskit 2.x, matplotlib, Google Colab

## Files

- `main.py` — Python implementation

## Run

```bash
python labs/lab02/main.py
```

## Test it

|0> sits at the north pole, X moves it to the south pole, H places it on the equator at +x, and the S gate rotates it around the equator while leaving the Z-basis probabilities at 50/50.

---

Full step-by-step instructions: **Learner Guide — Activity 2**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
