# Securing the Future with Quantum Computing and Cryptography

**WSQ Course Code:** TGS-2024043419
**Conducted by:** Tertiary Infotech Academy Pte Ltd (UEN 201200696W)
**Duration:** 4 days · 8 training hours per day (32 hours)
**Current version:** v13.0 (11 August 2026)

Courseware and hands-on lab suite for the WSQ course
[Securing the Future with Quantum Computing and Cryptography](https://www.tertiarycourses.com.sg/wsq-securing-the-future-with-quantum-computing-and-cryptography.html).

---

## Courseware

All artifacts are generated from a **single source of truth** so the slides, Lesson Plan,
Learner Guide and labs can never drift apart.

| Artifact | File |
|---|---|
| Trainer slide deck | `courseware/WSQ - Master Trainer Slides - Securing the Future with Quantum Computing and Cryptography - v13.0.pptx` (+ `.pdf`) |
| Lesson Plan | `courseware/LP-Securing the Future with Quantum Computing and Cryptography.docx` (+ `.pdf`) |
| Learner Guide | `courseware/LG-Securing the Future with Quantum Computing and Cryptography.docx` (+ `.pdf`) |
| Learner Guide (Markdown mirror) | `LG-Securing the Future with Quantum Computing and Cryptography.md` |
| Diagram assets | `courseware/assets/*.png` |

> The slide deck is deliberately **visual** and carries no step-by-step *lab*
> instructions. The full step-by-step for every activity lives in the **Learner Guide**.
> Mathematical **derivations**, by contrast, ARE stepped out slide by slide in the deck.

### Mathematical depth

The deck (262 slides) and Learner Guide (90 pages) carry the full theory, not an overview:

- **Prerequisites** — linear algebra and Dirac notation, inner/outer/tensor products,
  eigenvalues; unitary operators and their four properties; density matrices and the
  distinction between a superposition and a statistical mixture.
- **The five postulates of quantum mechanics** — one section each, with the formal
  statement, the mathematics, what it means in practice and why it matters.
- **Eleven complete derivations**, one algebra step at a time: phase kickback, Deutsch,
  Deutsch-Jozsa, quantum teleportation, the no-cloning theorem, BB84 security and the
  25% QBER, quantum error correction, Grover, Shor, CHSH and the QFT.
- **Quantum Phase Estimation** and the QFT built up from the classical DFT.
- **Post-quantum hardening** — Mosca's inequality, cryptographic inventory (CBOM),
  NIST FIPS 203/204/205, hybrid key exchange and crypto-agility.
- **Quantum security** — the threat model, an honest QKD vs PQC comparison, and QRNG.
- **Quantum computing and AI** — the four intersections, quantum ML assessed honestly,
  AI for quantum (calibration, ML error decoders), and the realistic outlook.

### Practice tool

[**QuantumLab Beginner**](https://alfredang.github.io/quantumlabs/) — the interactive
companion built by Tertiary Infotech Academy. 18 browser-based modules covering the
postulates, Bloch sphere, entanglement, a CHSH experiment, a drag-and-drop circuit
builder, a phase-kickback explorer, BB84 with an Eve toggle, and a 3-qubit QEC
Monte-Carlo. No install required.

Assessment papers and answer keys are **confidential** — they are distributed via Google
Drive and the LMS only, and are excluded from this repository.

### Rebuilding the courseware

```bash
python3 .claude/skills/courseware-build/build/make_charts.py       # diagram assets
bash    .claude/skills/courseware-build/build/build_courseware.sh  # PPT + LP + LG + PDFs
```

Content is edited in `.claude/skills/courseware-build/build/course_data.py` (metadata,
learning outcomes, topics, schedule) and `data_domain1.py` … `data_domain8.py`
(one file per topic, carrying that topic's hands-on activities).

---

## Learning outcomes

| | Outcome |
|---|---|
| LO1 | Design mathematical models required for quantum computing applications. |
| LO2 | Decide on appropriate physical methodologies specific to quantum computing problems. |
| LO3 | Direct two-level quantum models for quantum computing. |
| LO4 | Evaluate quantum computing applicability in the business context. |
| LO5 | Spearhead the application of quantum gates to quantum computing domains. |
| LO6 | Establish guidelines for selecting quantum computing algorithms. |
| LO7 | Synthesize quantum computing methodologies to address complex problems. |

## Course topics

| Topic | Title | Activities |
|---|---|---|
| 1 | Quantum Physics Fundamentals | 1 |
| 2 | Introduction to Quantum Computing Systems | 2–3 |
| 3 | Quantum Gates and Circuits | 4–5 |
| 4 | Quantum Protocols | 6–8 |
| 5 | Quantum Algorithms | 9–12 |
| 6 | Quantum Cryptography and Quantum Safety | 13–14 |
| 7 | Quantum Computing Applications and Use Cases | 15–16 |
| 8 | Quantum Error Correction | 17–18 |

---

## Hands-on activities

The 18 in-class activities live in [`labs/`](labs/), numbered `lab01`–`lab18` to match the
activity numbers used in the slides, Lesson Plan and Learner Guide:

| # | Activity | Folder |
|---|---|---|
| 1 | Linear Algebra for Quantum Mechanics in Python | [`labs/lab01/`](labs/lab01/) |
| 2 | Visualising a Qubit on the Bloch Sphere | [`labs/lab02/`](labs/lab02/) |
| 3 | Superposition and Entanglement on IBM Quantum | [`labs/lab03/`](labs/lab03/) |
| 4 | Building Circuits in IBM Quantum Composer | [`labs/lab04/`](labs/lab04/) |
| 5 | Quantum Gates and Bell/GHZ States with PennyLane | [`labs/lab05/`](labs/lab05/) |
| 6 | Quantum Teleportation | [`labs/lab06/`](labs/lab06/) |
| 7 | Superdense Coding Protocol | [`labs/lab07/`](labs/lab07/) |
| 8 | BB84 Quantum Key Distribution with Eavesdropping Detection | [`labs/lab08/`](labs/lab08/) |
| 9 | Deutsch and Deutsch-Jozsa Algorithms | [`labs/lab09/`](labs/lab09/) |
| 10 | Bernstein-Vazirani Algorithm | [`labs/lab10/`](labs/lab10/) |
| 11 | Grover's Search Algorithm | [`labs/lab11/`](labs/lab11/) |
| 12 | Quantum Fourier Transform | [`labs/lab12/`](labs/lab12/) |
| 13 | Shor's Algorithm and the Quantum Threat to RSA | [`labs/lab13/`](labs/lab13/) |
| 14 | Post-Quantum Cryptography Migration Assessment | [`labs/lab14/`](labs/lab14/) |
| 15 | Molecular Simulation with VQE (Healthcare & Science) | [`labs/lab15/`](labs/lab15/) |
| 16 | Portfolio Optimisation with QAOA (Finance) | [`labs/lab16/`](labs/lab16/) |
| 17 | Bit-Flip and Phase-Flip Error Correction Codes | [`labs/lab17/`](labs/lab17/) |
| 18 | Shor 9-Qubit and Steane 7-Qubit Codes | [`labs/lab18/`](labs/lab18/) |

Additional algorithms not used in class are kept in [`labs/bonus/`](labs/bonus/):
amplitude estimation, E91, HHL, quantum counting, quantum phase estimation, quantum walk,
Simon's algorithm, the SWAP test, and a combined QEC runner.

### Running the labs

```bash
pip install qiskit qiskit-ibm-runtime pennylane matplotlib pylatexenc python-dotenv numpy
```

Create `labs/.env` with your free [IBM Quantum](https://quantum.ibm.com) credentials:

```
IBM_QUANTUM_TOKEN=your_api_token_here
IBM_QUANTUM_INSTANCE=your_instance_here
```

Then run any activity:

```bash
python labs/lab01/main.py             # no IBM account needed
python labs/lab02/main.py             # no IBM account needed
python labs/lab03/main.py             # local simulator
python labs/lab03/main.py --hardware  # real IBM Quantum device
```

Every lab prints a **Test it** block stating exactly what a correct run looks like.

`.qasm` files can be loaded directly into
[IBM Quantum Composer](https://quantum.ibm.com/composer).

---

## Prerequisites

- Computer operation proficiency and a minimum Polytechnic Diploma.
- Basic programming skill, preferably Python.
- Minimum 1 year of working experience.
- Windows or Mac laptop; free Google Colab and IBM Quantum accounts.

## Assessment

- **Written Assessment (WA)** — Short-Answer Questions, 1 hour, open book.
- **Practical Performance (PP)** — hands-on quantum tasks, 1 hour, open book.
- Minimum 75% attendance is required for assessment and funding eligibility.

---

© 2026 Tertiary Infotech Academy Pte Ltd. All rights reserved. · [tertiarycourses.com.sg](https://www.tertiarycourses.com.sg)
