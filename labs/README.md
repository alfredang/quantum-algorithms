# Quantum Labs — Securing the Future with Quantum Computing and Cryptography

Hands-on lab suite for WSQ course **TGS-2024043419**, implemented with Qiskit and run on
the IBM Quantum Platform.

The **18 in-class activities** are numbered `lab01`–`lab18`, matching the activity numbers in
the slide deck, Lesson Plan and Learner Guide. Each folder holds its Python implementation,
any OpenQASM circuits, and a README.

Algorithms not used in class are kept in [`bonus/`](bonus/) for self-study — nothing has been
removed.

Full step-by-step instructions for every activity are in the **Learner Guide**.

## The 18 activities

| Lab | Activity | Topic | Files |
|---|---|---|---|
| [`lab01`](lab01/) | Linear Algebra for Quantum Mechanics in Python | 1 | `main.py` |
| [`lab02`](lab02/) | Visualising a Qubit on the Bloch Sphere | 2 | `main.py` |
| [`lab03`](lab03/) | Superposition and Entanglement on IBM Quantum | 2 | `main.py` |
| [`lab04`](lab04/) | Building Circuits in IBM Quantum Composer | 3 | `bell-state.qasm`, `main.py` |
| [`lab05`](lab05/) | Quantum Gates and Bell/GHZ States with PennyLane | 3 | `main.py` |
| [`lab06`](lab06/) | Quantum Teleportation | 4 | `main.py`, `teleportation-alt.qasm`, `teleportation.qasm` |
| [`lab07`](lab07/) | Superdense Coding Protocol | 4 | `main.py`, `superdense-coding.qasm` |
| [`lab08`](lab08/) | BB84 Quantum Key Distribution with Eavesdropping Detection | 4 | `bb84.qasm`, `main-with-eavesdropping.py`, `main.py` |
| [`lab09`](lab09/) | Deutsch and Deutsch-Jozsa Algorithms | 5 | `deutsch-jozsa.qasm`, `deutsch.qasm`, `main-deutsch-jozsa.py`, `main.py` |
| [`lab10`](lab10/) | Bernstein-Vazirani Algorithm | 5 | `bernstein-vazirani.qasm`, `main.py` |
| [`lab11`](lab11/) | Grover's Search Algorithm | 5 | `grover-2qubit.qasm`, `grover-3qubit.qasm`, `main.py` |
| [`lab12`](lab12/) | Quantum Fourier Transform | 5 | `main.py`, `qft-3qubit.qasm`, `qft-4qubit.qasm`, `qft-5qubit.qasm` |
| [`lab13`](lab13/) | Shor's Algorithm and the Quantum Threat to RSA | 6 | `main.py`, `shor-period-finding.qasm` |
| [`lab14`](lab14/) | Post-Quantum Cryptography Migration Assessment | 6 | `main.py` |
| [`lab15`](lab15/) | Molecular Simulation with VQE (Healthcare & Science) | 7 | `main.py`, `vqe-h2.qasm` |
| [`lab16`](lab16/) | Portfolio Optimisation with QAOA (Finance) | 7 | `main.py`, `qaoa-maxcut.qasm` |
| [`lab17`](lab17/) | Bit-Flip and Phase-Flip Error Correction Codes | 8 | `bit-flip-code.qasm`, `main-phase-flip.py`, `main.py`, `phase-flip-code.qasm` |
| [`lab18`](lab18/) | Shor 9-Qubit and Steane 7-Qubit Codes | 8 | `main-steane.py`, `main.py`, `shor-9qubit-code.qasm`, `steane-7qubit-code.qasm` |

## Setup

```bash
pip install qiskit qiskit-ibm-runtime pennylane matplotlib pylatexenc python-dotenv numpy
```

Create `labs/.env` with your free [IBM Quantum](https://quantum.ibm.com) credentials:

```
IBM_QUANTUM_TOKEN=your_api_token_here
IBM_QUANTUM_INSTANCE=your_instance_here
```

> `.env` is gitignored and is never uploaded — it holds a live API token.

## Running a lab

```bash
python labs/lab01/main.py    # no IBM account needed
python labs/lab02/main.py    # no IBM account needed
python labs/lab03/main.py    # local simulator
python labs/lab03/main.py --hardware   # real IBM Quantum device
```

Every lab prints a **Test it** block stating exactly what a correct run looks like.

`.qasm` files load directly into [IBM Quantum Composer](https://quantum.ibm.com/composer).

## Interactive practice

[**QuantumLab Beginner**](https://alfredang.github.io/quantumlabs/) — 18 browser-based modules
covering the postulates, Bloch sphere, entanglement, CHSH, a circuit builder, phase kickback,
BB84 with an Eve toggle and a 3-qubit QEC Monte-Carlo. No install required.

## Bonus material

[`bonus/`](bonus/) holds algorithms not used in the 18 in-class activities:
amplitude estimation, E91, HHL, quantum counting, quantum phase estimation, quantum walk,
Simon's algorithm, the SWAP test, and a combined QEC runner.

---

© 2026 Tertiary Infotech Academy Pte Ltd. All rights reserved.
