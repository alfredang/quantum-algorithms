"""
SWAP Test

Compares two quantum states to determine their overlap |⟨ψ|φ⟩|².
Useful for quantum machine learning, state comparison, and fingerprinting.
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


def create_swap_test_circuit(state1_params, state2_params):
    """
    Create SWAP test circuit to compare two single-qubit states.

    The SWAP test measures the overlap between |ψ⟩ and |φ⟩:
    P(ancilla=0) = (1 + |⟨ψ|φ⟩|²) / 2

    Args:
        state1_params: (theta, phi) for state |ψ⟩
        state2_params: (theta, phi) for state |φ⟩

    Returns:
        QuantumCircuit
    """
    # 3 qubits: 1 ancilla + 2 state qubits
    qc = QuantumCircuit(3, 1)

    # Prepare states using U3 gate
    # U3(θ, φ, λ)|0⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
    theta1, phi1 = state1_params
    theta2, phi2 = state2_params

    # Prepare |ψ⟩ on qubit 1
    qc.ry(theta1, 1)
    qc.rz(phi1, 1)

    # Prepare |φ⟩ on qubit 2
    qc.ry(theta2, 2)
    qc.rz(phi2, 2)

    qc.barrier()

    # SWAP test circuit
    # 1. Hadamard on ancilla
    qc.h(0)

    # 2. Controlled-SWAP (Fredkin gate)
    qc.cswap(0, 1, 2)

    # 3. Hadamard on ancilla
    qc.h(0)

    qc.barrier()

    # 4. Measure ancilla
    qc.measure(0, 0)

    return qc


def create_destructive_swap_test(state1_params, state2_params):
    """
    Create destructive SWAP test (uses fewer resources).

    Measures |⟨ψ|φ⟩|² directly using Bell measurement.

    Args:
        state1_params: (theta, phi) for state |ψ⟩
        state2_params: (theta, phi) for state |φ⟩

    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(2, 2)

    # Prepare states
    theta1, phi1 = state1_params
    theta2, phi2 = state2_params

    qc.ry(theta1, 0)
    qc.rz(phi1, 0)

    qc.ry(theta2, 1)
    qc.rz(phi2, 1)

    qc.barrier()

    # Bell measurement
    qc.cx(0, 1)
    qc.h(0)

    qc.barrier()

    qc.measure([0, 1], [0, 1])

    return qc


def compute_overlap_from_swap_test(counts, shots):
    """
    Compute state overlap from SWAP test measurements.

    P(0) = (1 + |⟨ψ|φ⟩|²) / 2
    |⟨ψ|φ⟩|² = 2*P(0) - 1

    Args:
        counts: Measurement counts
        shots: Total shots

    Returns:
        Estimated overlap |⟨ψ|φ⟩|²
    """
    count_0 = 0
    for bitstring, count in counts.items():
        bitstring = bitstring.replace(' ', '')
        if bitstring[-1] == '0':  # Ancilla is rightmost
            count_0 += count

    p_0 = count_0 / shots
    overlap = 2 * p_0 - 1

    return overlap, p_0


def compute_theoretical_overlap(state1_params, state2_params):
    """
    Compute theoretical overlap between two states.

    Args:
        state1_params: (theta, phi) for |ψ⟩
        state2_params: (theta, phi) for |φ⟩

    Returns:
        |⟨ψ|φ⟩|²
    """
    theta1, phi1 = state1_params
    theta2, phi2 = state2_params

    # |ψ⟩ = cos(θ₁/2)|0⟩ + e^(iφ₁)sin(θ₁/2)|1⟩
    # |φ⟩ = cos(θ₂/2)|0⟩ + e^(iφ₂)sin(θ₂/2)|1⟩

    # ⟨ψ|φ⟩ = cos(θ₁/2)cos(θ₂/2) + e^(i(φ₂-φ₁))sin(θ₁/2)sin(θ₂/2)

    inner = (math.cos(theta1/2) * math.cos(theta2/2) +
             np.exp(1j * (phi2 - phi1)) * math.sin(theta1/2) * math.sin(theta2/2))

    overlap = abs(inner) ** 2
    return overlap


def run_swap_test(test_cases, shots=1024):
    """
    Run SWAP test for multiple state pairs.

    Args:
        test_cases: List of (state1_params, state2_params, description)
        shots: Number of shots per test

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    results = []

    for state1_params, state2_params, description in test_cases:
        print(f"\nTest: {description}")

        # Create circuit
        qc = create_swap_test_circuit(state1_params, state2_params)

        # Theoretical overlap
        theory = compute_theoretical_overlap(state1_params, state2_params)
        print(f"  Theoretical |⟨ψ|φ⟩|²: {theory:.4f}")

        # Transpile and run
        transpiled = transpile(qc, backend, optimization_level=1)
        job = sampler.run([transpiled], shots=shots)
        print(f"  Job ID: {job.job_id()}")

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

        # Compute overlap
        overlap, p_0 = compute_overlap_from_swap_test(counts, shots)
        print(f"  Measured P(0): {p_0:.4f}")
        print(f"  Estimated |⟨ψ|φ⟩|²: {overlap:.4f}")

        results.append({
            'description': description,
            'state1_params': state1_params,
            'state2_params': state2_params,
            'theoretical_overlap': theory,
            'measured_overlap': overlap,
            'p_0': p_0,
            'counts': counts,
            'circuit': qc
        })

    return {
        'test_results': results,
        'backend': backend.name,
        'shots': shots
    }


def analyze_results(results):
    """Analyze SWAP test results."""
    print("\n" + "=" * 60)
    print("SWAP TEST RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Shots per test: {results['shots']}")

    print("\n" + "-" * 60)
    print("TEST SUMMARY")
    print("-" * 60)

    for test in results['test_results']:
        print(f"\n{test['description']}:")
        print(f"  |ψ⟩ params: θ={test['state1_params'][0]:.3f}, φ={test['state1_params'][1]:.3f}")
        print(f"  |φ⟩ params: θ={test['state2_params'][0]:.3f}, φ={test['state2_params'][1]:.3f}")
        print(f"  Theoretical overlap: {test['theoretical_overlap']:.4f}")
        print(f"  Measured overlap: {test['measured_overlap']:.4f}")
        error = abs(test['theoretical_overlap'] - test['measured_overlap'])
        print(f"  Error: {error:.4f}")

    # Show circuit for first test
    print("\nSWAP test circuit structure:")
    print(results['test_results'][0]['circuit'].draw())

    print(f"\nSWAP test explanation:")
    print("  1. Prepare two states |ψ⟩ and |φ⟩")
    print("  2. Apply Hadamard to ancilla: |0⟩ → |+⟩")
    print("  3. Controlled-SWAP: |0⟩|ψ⟩|φ⟩ + |1⟩|φ⟩|ψ⟩")
    print("  4. Apply Hadamard to ancilla")
    print("  5. Measure ancilla")
    print("  6. P(0) = (1 + |⟨ψ|φ⟩|²) / 2")

    print(f"\nApplications:")
    print("  - Quantum fingerprinting")
    print("  - Quantum machine learning (kernel methods)")
    print("  - Quantum state tomography")
    print("  - Quantum fidelity estimation")


if __name__ == "__main__":
    try:
        print("Executing SWAP Test on IBM Quantum hardware...")
        print("\nThe SWAP test measures the overlap between two quantum states")
        print("using the formula P(0) = (1 + |⟨ψ|φ⟩|²) / 2\n")

        # Define test cases
        test_cases = [
            # (state1_params, state2_params, description)
            ((0, 0), (0, 0), "Identical states |0⟩ vs |0⟩"),
            ((math.pi, 0), (math.pi, 0), "Identical states |1⟩ vs |1⟩"),
            ((0, 0), (math.pi, 0), "Orthogonal states |0⟩ vs |1⟩"),
            ((math.pi/2, 0), (math.pi/2, 0), "Identical |+⟩ states"),
            ((math.pi/2, 0), (math.pi/2, math.pi), "Orthogonal |+⟩ vs |-⟩"),
        ]

        results = run_swap_test(test_cases, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
