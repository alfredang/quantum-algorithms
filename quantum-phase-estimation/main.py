"""
Quantum Phase Estimation (QPE)

Estimates the phase φ in U|ψ⟩ = e^(2πiφ)|ψ⟩ where |ψ⟩ is an eigenstate of U.
This is a fundamental subroutine used in Shor's algorithm, HHL, and many others.
"""

import os
import math
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_qpe_circuit(n_counting_qubits, phase):
    """
    Create a Quantum Phase Estimation circuit.

    The circuit estimates the phase φ where U|ψ⟩ = e^(2πiφ)|ψ⟩.
    For demonstration, we use a simple phase gate U = P(2πφ) and |ψ⟩ = |1⟩.

    Args:
        n_counting_qubits: Number of qubits for phase estimation precision
        phase: The phase to estimate (0 to 1)

    Returns:
        QuantumCircuit implementing QPE
    """
    # n counting qubits + 1 target qubit
    qc = QuantumCircuit(n_counting_qubits + 1, n_counting_qubits)

    # Prepare eigenstate |1⟩ on target qubit
    qc.x(n_counting_qubits)

    # Apply Hadamard to all counting qubits
    for i in range(n_counting_qubits):
        qc.h(i)

    qc.barrier()

    # Apply controlled-U^(2^j) operations
    # U = P(2πφ), so U^(2^j) = P(2^j * 2πφ)
    for j in range(n_counting_qubits):
        # Controlled phase rotation
        angle = 2 * math.pi * phase * (2 ** j)
        qc.cp(angle, j, n_counting_qubits)

    qc.barrier()

    # Inverse QFT on counting qubits
    for j in range(n_counting_qubits // 2):
        qc.swap(j, n_counting_qubits - j - 1)

    for j in range(n_counting_qubits):
        for k in range(j):
            qc.cp(-math.pi / (2 ** (j - k)), k, j)
        qc.h(j)

    qc.barrier()

    # Measure counting qubits
    qc.measure(range(n_counting_qubits), range(n_counting_qubits))

    return qc


def binary_to_phase(bitstring, n_qubits):
    """Convert measurement result to estimated phase."""
    value = int(bitstring, 2)
    return value / (2 ** n_qubits)


def run_qpe(n_counting_qubits=3, phase=0.25, shots=1024):
    """
    Run Quantum Phase Estimation on IBM Quantum hardware.

    Args:
        n_counting_qubits: Number of counting qubits (determines precision)
        phase: The actual phase to estimate (between 0 and 1)
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_counting_qubits + 1)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_qpe_circuit(n_counting_qubits, phase)

    print(f"\nPhase to estimate: {phase}")
    print(f"Counting qubits: {n_counting_qubits}")
    print(f"Precision: 1/{2**n_counting_qubits} = {1/(2**n_counting_qubits):.4f}")
    print("\nCircuit:")
    print(qc.draw())

    # Transpile for the backend
    transpiled_qc = transpile(qc, backend, optimization_level=1)
    print(f"\nTranspiled circuit depth: {transpiled_qc.depth()}")

    # Run on hardware
    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled_qc], shots=shots)
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
        'phase': phase,
        'n_counting_qubits': n_counting_qubits,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze QPE results."""
    print("\n" + "=" * 60)
    print("QUANTUM PHASE ESTIMATION RESULTS")
    print("=" * 60)

    phase = results['phase']
    n_qubits = results['n_counting_qubits']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Actual phase: {phase}")
    print(f"Counting qubits: {n_qubits}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    estimated_phases = []
    for bitstring, count in sorted_counts[:10]:
        est_phase = binary_to_phase(bitstring, n_qubits)
        error = abs(est_phase - phase)
        percentage = count / shots * 100
        estimated_phases.append((est_phase, count))
        print(f"  {bitstring} -> phase={est_phase:.4f} (error={error:.4f}): {count} ({percentage:.1f}%)")

    # Best estimate (most common)
    best_bitstring = sorted_counts[0][0]
    best_estimate = binary_to_phase(best_bitstring, n_qubits)
    best_error = abs(best_estimate - phase)

    print(f"\nPhase estimation:")
    print(f"  Actual phase: {phase:.4f}")
    print(f"  Best estimate: {best_estimate:.4f}")
    print(f"  Error: {best_error:.4f}")
    print(f"  Theoretical precision: {1/(2**n_qubits):.4f}")

    if best_error <= 1 / (2 ** n_qubits):
        print(f"\n✓ Success! Estimated phase within theoretical precision.")
    else:
        print(f"\n✗ Error exceeds theoretical precision (likely due to hardware noise).")

    print(f"\nQuantum advantage:")
    print(f"  QPE achieves precision ε with O(1/ε) operations")
    print(f"  Classical phase estimation requires O(1/ε²) samples")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Quantum Phase Estimation on IBM Quantum hardware...")
        print("\nQPE estimates the phase φ where U|ψ⟩ = e^(2πiφ)|ψ⟩")
        print("This is a fundamental subroutine for Shor's algorithm, HHL, and more.\n")

        # Configuration
        n_counting_qubits = 3  # Precision: 1/2^3 = 0.125
        phase = 0.25  # Phase to estimate (try 0.125, 0.375, etc.)

        results = run_qpe(n_counting_qubits, phase, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
