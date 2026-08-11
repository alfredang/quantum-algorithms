"""
Quantum Amplitude Estimation (QAE)

Estimates the amplitude a of a quantum state preparation A|0⟩ = √(1-a)|ψ₀⟩ + √a|ψ₁⟩
Provides quadratic speedup over classical Monte Carlo methods.
"""

import os
import math
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_amplitude_operator(n_qubits, target_amplitude):
    """
    Create an amplitude preparation operator A.

    A|0⟩ = √(1-a)|ψ₀⟩ + √a|ψ₁⟩

    For demonstration, we use Ry rotation to set amplitude.
    """
    qc = QuantumCircuit(n_qubits, name="A")

    # Ry(2θ)|0⟩ = cos(θ)|0⟩ + sin(θ)|1⟩
    # We want sin²(θ) = a, so θ = arcsin(√a)
    theta = 2 * math.asin(math.sqrt(target_amplitude))
    qc.ry(theta, 0)

    return qc


def create_grover_like_operator(amplitude_op):
    """
    Create the Grover-like operator Q = A S₀ A† Sf

    This operator has eigenvalues e^(±2iθ) where sin²(θ) = a
    """
    n_qubits = amplitude_op.num_qubits
    qc = QuantumCircuit(n_qubits, name="Q")

    # Sf: flip phase of |1⟩ state
    qc.z(0)

    # A†
    qc.compose(amplitude_op.inverse(), inplace=True)

    # S₀: flip phase of |0⟩ state
    qc.x(0)
    qc.z(0)
    qc.x(0)

    # A
    qc.compose(amplitude_op, inplace=True)

    return qc


def create_amplitude_estimation_circuit(n_counting_qubits, target_amplitude):
    """
    Create Quantum Amplitude Estimation circuit.

    Uses QPE to estimate the eigenvalue of Q, revealing the amplitude a.

    Args:
        n_counting_qubits: Number of counting qubits for precision
        target_amplitude: The amplitude to estimate

    Returns:
        QuantumCircuit for amplitude estimation
    """
    # 1 state qubit + n counting qubits
    qc = QuantumCircuit(n_counting_qubits + 1, n_counting_qubits)

    # Create amplitude operator
    amplitude_op = create_amplitude_operator(1, target_amplitude)

    # Prepare initial state A|0⟩
    qc.compose(amplitude_op, [n_counting_qubits], inplace=True)

    # Apply Hadamard to counting qubits
    for i in range(n_counting_qubits):
        qc.h(i)

    qc.barrier()

    # Create Q operator
    Q = create_grover_like_operator(amplitude_op)
    controlled_Q = Q.control(1)

    # Apply controlled-Q^(2^j) operations
    for j in range(n_counting_qubits):
        power = 2 ** j
        for _ in range(power):
            qc.compose(controlled_Q, [j, n_counting_qubits], inplace=True)

    qc.barrier()

    # Inverse QFT
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


def estimate_amplitude(measurement, n_counting_qubits):
    """
    Convert QPE measurement to amplitude estimate.

    The measurement gives θ where the eigenvalue is e^(2πiθ)
    and a = sin²(πθ)
    """
    theta = int(measurement, 2) / (2 ** n_counting_qubits)
    amplitude = math.sin(math.pi * theta) ** 2
    return amplitude


def run_amplitude_estimation(n_counting_qubits=3, target_amplitude=0.25, shots=1024):
    """
    Run Quantum Amplitude Estimation on IBM Quantum hardware.

    Args:
        n_counting_qubits: Number of counting qubits
        target_amplitude: The amplitude to estimate
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
    qc = create_amplitude_estimation_circuit(n_counting_qubits, target_amplitude)

    print(f"\nTarget amplitude: {target_amplitude}")
    print(f"Counting qubits: {n_counting_qubits}")
    print(f"Precision: ~{1/(2**n_counting_qubits):.4f}")
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
        'target_amplitude': target_amplitude,
        'n_counting_qubits': n_counting_qubits,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze amplitude estimation results."""
    print("\n" + "=" * 60)
    print("QUANTUM AMPLITUDE ESTIMATION RESULTS")
    print("=" * 60)

    target = results['target_amplitude']
    n_counting = results['n_counting_qubits']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Target amplitude: {target}")
    print(f"Counting qubits: {n_counting}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    for bitstring, count in sorted_counts[:10]:
        est = estimate_amplitude(bitstring, n_counting)
        error = abs(est - target)
        percentage = count / shots * 100
        print(f"  {bitstring} -> amplitude={est:.4f} (error={error:.4f}): {count} ({percentage:.1f}%)")

    # Best estimate
    best_bitstring = sorted_counts[0][0]
    best_estimate = estimate_amplitude(best_bitstring, n_counting)
    best_error = abs(best_estimate - target)

    print(f"\nAmplitude estimation:")
    print(f"  Target amplitude: {target:.4f}")
    print(f"  Best estimate: {best_estimate:.4f}")
    print(f"  Error: {best_error:.4f}")

    if best_error < 0.1:
        print(f"\n✓ Good estimate! Error within 10%.")
    else:
        print(f"\n✗ Larger error due to hardware noise or precision limit.")

    print(f"\nQuantum advantage:")
    print(f"  Classical Monte Carlo: O(1/ε²) samples for precision ε")
    print(f"  Quantum Amplitude Estimation: O(1/ε) operations")
    print(f"  Quadratic speedup for estimating probabilities!")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Quantum Amplitude Estimation on IBM Quantum hardware...")
        print("\nQAE estimates the amplitude a where A|0⟩ = √(1-a)|ψ₀⟩ + √a|ψ₁⟩")
        print("This provides quadratic speedup over classical Monte Carlo.\n")

        # Configuration
        n_counting_qubits = 3
        target_amplitude = 0.25  # Amplitude to estimate

        results = run_amplitude_estimation(n_counting_qubits, target_amplitude, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
