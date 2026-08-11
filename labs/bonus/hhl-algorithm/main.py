"""
Harrow-Hassidim-Lloyd (HHL) Algorithm

Solves linear systems Ax = b with exponential speedup for sparse matrices.
Demonstrates the core quantum linear systems algorithm.
"""

import os
import math
import numpy as np
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_simple_hhl_circuit():
    """
    Create a simplified HHL circuit for the system:
    A = [[1, -1/3], [-1/3, 1]]
    b = [1, 0]

    This is a 4-qubit implementation:
    - q[0]: ancilla for eigenvalue inversion
    - q[1]: clock qubit for QPE
    - q[2]: state qubit for |b⟩

    Returns:
        QuantumCircuit for simplified HHL
    """
    n_qubits = 3
    qc = QuantumCircuit(n_qubits, 1)

    # Step 1: Prepare initial state |b⟩
    # |b⟩ = |1⟩ corresponds to b = [1, 0]
    # (q[2] starts in |0⟩)

    # Step 2: QPE to estimate eigenvalues
    # Apply Hadamard to clock qubit
    qc.h(1)

    qc.barrier()

    # Controlled-U where U = e^(iAt)
    # For our simple A, the controlled evolution can be approximated
    # Using simplified controlled rotation
    qc.cp(math.pi / 2, 1, 2)

    qc.barrier()

    # Step 3: Apply inverse QFT to clock register
    qc.h(1)

    qc.barrier()

    # Step 4: Controlled rotation based on eigenvalue
    # Rotate ancilla proportional to 1/eigenvalue
    # For eigenvalue λ, rotate by arcsin(C/λ) where C is normalization

    # Controlled-Ry based on clock qubit state
    # When clock = |1⟩, eigenvalue is larger, need smaller rotation
    # When clock = |0⟩, eigenvalue is smaller, need larger rotation

    # Controlled rotation: ancilla rotation conditioned on clock
    qc.cry(math.pi / 3, 1, 0)  # When clock=|1⟩
    qc.x(1)
    qc.cry(math.pi / 2, 1, 0)  # When clock=|0⟩
    qc.x(1)

    qc.barrier()

    # Step 5: Uncompute QPE (simplified)
    qc.h(1)
    qc.cp(-math.pi / 2, 1, 2)
    qc.h(1)

    qc.barrier()

    # Step 6: Measure ancilla
    # Success when ancilla = |1⟩
    qc.measure(0, 0)

    return qc


def create_hhl_2x2_circuit():
    """
    Create HHL circuit for solving 2x2 system.

    For A = [[3, 1], [1, 3]] / 4 and b = [1, 0]
    Eigenvalues: λ₁ = 1, λ₂ = 1/2
    Solution: x ∝ [3, -1]

    Uses 4 qubits:
    - q[0]: ancilla
    - q[1-2]: clock register (2 qubits)
    - q[3]: state register

    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(4, 3)

    # Prepare |b⟩ = |0⟩ (first basis state)
    # q[3] already in |0⟩

    # QPE: Hadamard on clock qubits
    qc.h(1)
    qc.h(2)

    qc.barrier()

    # Controlled-U operations
    # U = e^(2πiA) for eigenvalue estimation
    # For our matrix, this maps eigenvalues to phases

    # Controlled-U^1 from q[1]
    qc.cp(math.pi / 2, 1, 3)
    qc.cx(1, 3)
    qc.cp(math.pi / 4, 1, 3)
    qc.cx(1, 3)

    # Controlled-U^2 from q[2]
    qc.cp(math.pi, 2, 3)
    qc.cx(2, 3)
    qc.cp(math.pi / 2, 2, 3)
    qc.cx(2, 3)

    qc.barrier()

    # Inverse QFT on clock register
    qc.swap(1, 2)
    qc.h(1)
    qc.cp(-math.pi / 2, 1, 2)
    qc.h(2)

    qc.barrier()

    # Eigenvalue inversion: controlled rotations on ancilla
    # Rotate proportional to 1/λ
    # λ₁ corresponds to clock state |01⟩, λ₂ to |10⟩

    # Multi-controlled rotation based on clock state
    # Simplified: apply rotations conditioned on clock

    # When clock = |01⟩ (λ = 1): arcsin(C/1)
    qc.x(2)
    qc.ccx(1, 2, 0)  # Simplified - mark ancilla
    qc.cry(math.pi / 3, 1, 0)
    qc.x(2)

    # When clock = |10⟩ (λ = 1/2): arcsin(C/0.5) = 2*arcsin(C)
    qc.x(1)
    qc.cry(2 * math.pi / 3, 2, 0)
    qc.x(1)

    qc.barrier()

    # Uncompute QPE (simplified - just barriers for visualization)
    qc.h(2)
    qc.cp(math.pi / 2, 1, 2)
    qc.h(1)
    qc.swap(1, 2)

    qc.barrier()

    # Measure
    qc.measure(0, 0)  # Ancilla - post-select on |1⟩
    qc.measure(3, 1)  # Solution state
    qc.measure(1, 2)  # Clock for verification

    return qc


def run_hhl(shots=1024):
    """
    Run simplified HHL algorithm on IBM Quantum hardware.

    Args:
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=4)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_simple_hhl_circuit()

    print("\nSimplified HHL Algorithm")
    print("Solving Ax = b where:")
    print("  A = [[1, -1/3], [-1/3, 1]]")
    print("  b = [1, 0]")
    print("\nCircuit:")
    print(qc.draw())

    # Transpile
    transpiled = transpile(qc, backend, optimization_level=1)
    print(f"\nTranspiled circuit depth: {transpiled.depth()}")

    # Run
    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled], shots=shots)
    print(f"Job submitted: {job.job_id()}")
    print("Waiting for results...")

    result = job.result()

    # Extract counts
    pub_result = result[0]
    counts = {}
    for attr in dir(pub_result.data):
        if not attr.startswith('_'):
            try:
                data_obj = getattr(pub_result.data, attr)
                if hasattr(data_obj, 'get_counts'):
                    counts = data_obj.get_counts()
                    if counts:
                        break
            except:
                pass

    return {
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze HHL results."""
    print("\n" + "=" * 60)
    print("HHL ALGORITHM RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Total shots: {results['shots']}")

    counts = results['counts']
    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    total = results['shots']

    success_count = 0
    for bitstring, count in sorted_counts:
        bitstring = bitstring.replace(' ', '')
        percentage = count / total * 100
        # Check if ancilla (rightmost bit) is 1 (success)
        if bitstring[-1] == '1':
            status = "SUCCESS"
            success_count += count
        else:
            status = "fail"
        print(f"  {bitstring}: {count} ({percentage:.1f}%) - {status}")

    success_rate = success_count / total * 100
    print(f"\nSuccess rate (ancilla=1): {success_rate:.1f}%")

    print(f"\nHHL algorithm explanation:")
    print("  1. Encode |b⟩ in quantum state")
    print("  2. QPE: extract eigenvalues λⱼ of A into clock register")
    print("  3. Rotate ancilla by arcsin(C/λⱼ)")
    print("  4. Uncompute QPE")
    print("  5. Measure ancilla - post-select on |1⟩")
    print("  6. Result: |x⟩ = A⁻¹|b⟩ (normalized)")

    print(f"\nComplexity:")
    print("  Classical: O(N³) or O(N s log(1/ε)) for iterative methods")
    print("  Quantum HHL: O(s² κ² log(N) / ε)")
    print("  where s=sparsity, κ=condition number, ε=precision")

    print(f"\nApplications:")
    print("  - Machine learning (least squares)")
    print("  - Finite element analysis")
    print("  - Optimization problems")
    print("  - Quantum chemistry")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing HHL Algorithm on IBM Quantum hardware...")
        print("\nHHL solves linear systems Ax = b with exponential speedup")
        print("for sparse, well-conditioned matrices.\n")

        results = run_hhl(shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
