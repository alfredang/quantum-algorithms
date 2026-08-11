# Lab 08 — BB84 Quantum Key Distribution with Eavesdropping Detection

**Topic 4:** Quantum Protocols  
**Maps to:** LO7 — Synthesize quantum methodologies to address complex problems

Run the BB84 protocol end to end: random bit and basis selection, quantum transmission, basis sifting and key extraction — then repeat it with an eavesdropper present and measure the error rate that exposes the attack.

## What you'll build

A working BB84 implementation producing a shared secret key, plus a comparison run showing the ~25% error rate introduced by an intercept-resend eavesdropper.

**Tools:** Qiskit 2.x, IBM Quantum Runtime, Python

## Files

- `bb84.qasm` — OpenQASM circuit — load directly into IBM Quantum Composer
- `main-with-eavesdropping.py` — Python implementation
- `main.py` — Python implementation

## Run

```bash
python labs/lab08/main.py
```

## Test it

Without an eavesdropper the sifted key error rate is near zero (bounded only by hardware noise); with the intercept-resend eavesdropper the error rate rises to roughly 25%, which is the signal to abort and discard the key.

---

Full step-by-step instructions: **Learner Guide — Activity 8**.

Interactive practice: [QuantumLab Beginner](https://alfredang.github.io/quantumlabs/)
