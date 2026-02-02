# Quantum Algorithms

A collection of quantum computing algorithms implemented using Qiskit and executed on IBM Quantum hardware.

## Algorithms Implemented

### Fundamental Algorithms
- **Deutsch Algorithm** - Determines if a function is constant or balanced with 1 query
- **Deutsch-Jozsa Algorithm** - Generalized Deutsch algorithm for n-bit functions
- **Bernstein-Vazirani Algorithm** - Finds hidden string s in f(x) = s·x (mod 2)
- **Simon's Algorithm** - Exponential speedup for finding hidden period

### Search & Optimization
- **Grover's Algorithm** - Quadratic speedup for unstructured search O(√N)
- **QAOA** - Quantum Approximate Optimization Algorithm for combinatorial optimization
- **Quantum Walk** - Discrete-time quantum walk with quadratic speedup for graph search

### Quantum Transforms & Estimation
- **Quantum Fourier Transform (QFT)** - Basis for many quantum algorithms
- **Quantum Phase Estimation (QPE)** - Estimates eigenvalues of unitary operators
- **Quantum Counting** - Combines Grover and QPE to count solutions
- **Amplitude Estimation** - Quadratic speedup over classical Monte Carlo

### Factoring & Linear Systems
- **Shor's Algorithm** - Integer factorization (simplified demonstration)
- **HHL Algorithm** - Solves linear systems Ax=b with exponential speedup

### Variational Algorithms (NISQ)
- **VQE** - Variational Quantum Eigensolver for finding ground state energies
- **QAOA** - Variational algorithm for combinatorial optimization

### Quantum Communication
- **Quantum Teleportation** - Transfer quantum state using entanglement
- **Superdense Coding** - Send 2 classical bits using 1 qubit
- **BB84 Protocol** - Quantum key distribution
  - Standard BB84 (without eavesdropping)
  - BB84 with eavesdropping detection
- **E91 Protocol** - Entanglement-based QKD with Bell inequality security

### State Comparison
- **SWAP Test** - Compares quantum states to measure overlap |⟨ψ|φ⟩|²

### Error Correction
- **Bit-Flip Code** - 3-qubit code protecting against X errors
- **Phase-Flip Code** - 3-qubit code protecting against Z errors
- **Shor's 9-Qubit Code** - First QEC code, protects against arbitrary single-qubit errors
- **Steane's 7-Qubit Code** - CSS code based on Hamming code, more efficient than Shor

## Setup

### Prerequisites
- Python 3.13+
- IBM Quantum account ([sign up here](https://quantum.ibm.com/))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/alfredang/quantum-algorithms.git
cd quantum-algorithms
```

2. Install dependencies:
```bash
pip install -e .
# or using uv:
uv sync
```

3. Create a `.env` file with your IBM Quantum credentials:
```bash
cp .env.example .env
# Edit .env with your credentials
```

Your `.env` file should contain:
```
IBM_QUANTUM_TOKEN=your_api_token_here
IBM_QUANTUM_INSTANCE=your_instance_here
```

Get your API token from: https://quantum.ibm.com/

## Usage

### Run with Python (IBM Quantum Hardware)
```bash
python deutsch-algorithm/main.py
python grover-algorithm/main.py
python vqe/main.py
python qaoa/main.py
python e91-protocol/main.py
# etc.
```

### IBM Quantum Composer
Each algorithm folder includes `.qasm` files that can be uploaded directly to [IBM Quantum Composer](https://quantum.ibm.com/composer):

| Algorithm | QASM File |
|-----------|-----------|
| Deutsch | `deutsch-algorithm/deutsch.qasm` |
| Deutsch-Jozsa | `deutsch-jozsa-algorithm/deutsch-jozsa.qasm` |
| Bernstein-Vazirani | `bernstein-vazirani-algorithm/bernstein-vazirani.qasm` |
| Simon | `simon-algorithm/simon.qasm` |
| Grover (2-qubit) | `grover-algorithm/grover-2qubit.qasm` |
| Grover (3-qubit) | `grover-algorithm/grover-3qubit.qasm` |
| QFT (3-qubit) | `quantum-fourier-transform/qft-3qubit.qasm` |
| QFT (4-qubit) | `quantum-fourier-transform/qft-4qubit.qasm` |
| QFT (5-qubit) | `quantum-fourier-transform/qft-5qubit.qasm` |
| QPE (3-qubit) | `quantum-phase-estimation/qpe-3qubit.qasm` |
| Quantum Counting | `quantum-counting/quantum-counting.qasm` |
| Amplitude Estimation | `amplitude-estimation/amplitude-estimation.qasm` |
| Shor (Period Finding) | `shor-algorithm/shor-period-finding.qasm` |
| HHL | `hhl-algorithm/hhl-simple.qasm` |
| VQE (H₂) | `vqe/vqe-h2.qasm` |
| QAOA (Max-Cut) | `qaoa/qaoa-maxcut.qasm` |
| Quantum Walk | `quantum-walk/quantum-walk.qasm` |
| SWAP Test | `swap-test/swap-test.qasm` |
| Teleportation | `quantum-teleportation/teleportation.qasm` |
| Superdense Coding | `superdense-coding/superdense-coding.qasm` |
| BB84 | `bb84/bb84.qasm` |
| E91 | `e91-protocol/e91.qasm` |
| Bit-Flip Code | `quantum-error-correction/bit-flip-code/bit-flip-code.qasm` |
| Phase-Flip Code | `quantum-error-correction/phase-flip-code/phase-flip-code.qasm` |
| Shor's 9-Qubit Code | `quantum-error-correction/shor-9qubit-code/shor-9qubit-code.qasm` |
| Steane's 7-Qubit Code | `quantum-error-correction/steane-7qubit-code/steane-7qubit-code.qasm` |

## Project Structure

```
quantum-algorithms/
├── amplitude-estimation/
├── bernstein-vazirani-algorithm/
├── bb84/
│   ├── bb84-with-eavesdropping/
│   └── bb84-without-eavesdropping/
├── deutsch-algorithm/
├── deutsch-jozsa-algorithm/
├── e91-protocol/
├── grover-algorithm/
├── hhl-algorithm/
├── qaoa/
├── quantum-counting/
├── quantum-error-correction/
│   ├── bit-flip-code/
│   ├── phase-flip-code/
│   ├── shor-9qubit-code/
│   └── steane-7qubit-code/
├── quantum-fourier-transform/
├── quantum-phase-estimation/
├── quantum-teleportation/
├── quantum-walk/
├── shor-algorithm/
├── simon-algorithm/
├── superdense-coding/
├── swap-test/
├── vqe/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## License

MIT
