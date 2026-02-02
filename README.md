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

### Quantum Transforms
- **Quantum Fourier Transform (QFT)** - Basis for many quantum algorithms
- **Shor's Algorithm** - Integer factorization (simplified demonstration)

### Quantum Communication
- **Quantum Teleportation** - Transfer quantum state using entanglement
- **Superdense Coding** - Send 2 classical bits using 1 qubit
- **BB84 Protocol** - Quantum key distribution
  - Standard BB84 (without eavesdropping)
  - BB84 with eavesdropping detection

### Error Correction
- **Bit-Flip Code** - 3-qubit code protecting against X errors
- **Phase-Flip Code** - 3-qubit code protecting against Z errors

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
python bb84/bb84-with-eavesdropping/main.py
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
| Shor (Period Finding) | `shor-algorithm/shor-period-finding.qasm` |
| Teleportation | `quantum-teleportation/teleportation.qasm` |
| Superdense Coding | `superdense-coding/superdense-coding.qasm` |
| BB84 | `bb84/bb84.qasm` |
| Bit-Flip Code | `quantum-error-correction/bit-flip-code/bit-flip-code.qasm` |
| Phase-Flip Code | `quantum-error-correction/phase-flip-code/phase-flip-code.qasm` |

## Project Structure

```
quantum-algorithms/
├── bernstein-vazirani-algorithm/
├── bb84/
│   ├── bb84-with-eavesdropping/
│   └── bb84-without-eavesdropping/
├── deutsch-algorithm/
├── deutsch-jozsa-algorithm/
├── quantum-error-correction/
│   ├── bit-flip-code/
│   └── phase-flip-code/
├── grover-algorithm/
├── quantum-fourier-transform/
├── quantum-teleportation/
├── shor-algorithm/
├── simon-algorithm/
├── superdense-coding/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## License

MIT
