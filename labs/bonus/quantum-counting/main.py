"""
Quantum Counting Algorithm

Combines Grover's algorithm with Quantum Phase Estimation to count
the number of solutions to a search problem.
"""

import os
import math
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_grover_operator(n_qubits, marked_states):
    """
    Create Grover operator G = -H⊗n S₀ H⊗n Sf
    where Sf is the oracle and S₀ is the zero-state phase flip.
    """
    qc = QuantumCircuit(n_qubits, name="Grover")

    # Oracle: flip phase of marked states
    for state in marked_states:
        # Convert to binary and apply X gates to flip zeros
        state_bin = format(state, f'0{n_qubits}b')
        for i, bit in enumerate(reversed(state_bin)):
            if bit == '0':
                qc.x(i)

        # Multi-controlled Z
        if n_qubits == 2:
            qc.cz(0, 1)
        else:
            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)

        # Undo X gates
        for i, bit in enumerate(reversed(state_bin)):
            if bit == '0':
                qc.x(i)

    # Diffusion operator
    for i in range(n_qubits):
        qc.h(i)
        qc.x(i)

    if n_qubits == 2:
        qc.cz(0, 1)
    else:
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)

    for i in range(n_qubits):
        qc.x(i)
        qc.h(i)

    return qc


def create_quantum_counting_circuit(n_search_qubits, n_counting_qubits, marked_states):
    """
    Create Quantum Counting circuit.

    Uses QPE to estimate the eigenvalue of the Grover operator,
    which reveals the number of solutions.

    Args:
        n_search_qubits: Number of qubits for search space
        n_counting_qubits: Number of qubits for counting precision
        marked_states: List of marked states (solutions)

    Returns:
        QuantumCircuit for quantum counting
    """
    total_qubits = n_counting_qubits + n_search_qubits
    qc = QuantumCircuit(total_qubits, n_counting_qubits)

    # Initialize search register in uniform superposition
    for i in range(n_counting_qubits, total_qubits):
        qc.h(i)

    # Apply Hadamard to counting qubits
    for i in range(n_counting_qubits):
        qc.h(i)

    qc.barrier()

    # Create Grover operator
    grover_op = create_grover_operator(n_search_qubits, marked_states)
    controlled_grover = grover_op.control(1)

    # Apply controlled-G^(2^j) operations
    for j in range(n_counting_qubits):
        power = 2 ** j
        for _ in range(power):
            qc.compose(
                controlled_grover,
                [j] + list(range(n_counting_qubits, total_qubits)),
                inplace=True
            )

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


def estimate_count(measurement, n_counting_qubits, n_search_qubits):
    """
    Estimate the number of solutions from QPE measurement.

    The eigenvalue of G is e^(2πiθ) where sin²(πθ) = M/N
    M = number of solutions, N = search space size
    """
    theta = int(measurement, 2) / (2 ** n_counting_qubits)
    N = 2 ** n_search_qubits

    # M = N * sin²(πθ)
    M = N * (math.sin(math.pi * theta) ** 2)

    return round(M)


def run_quantum_counting(n_search_qubits=2, n_counting_qubits=3, marked_states=None, shots=1024):
    """
    Run Quantum Counting on IBM Quantum hardware.

    Args:
        n_search_qubits: Number of qubits for search space
        n_counting_qubits: Number of counting qubits
        marked_states: List of marked states (default: [3])
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    if marked_states is None:
        marked_states = [3]  # Default: mark state |11⟩

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    total_qubits = n_counting_qubits + n_search_qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=total_qubits)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_quantum_counting_circuit(n_search_qubits, n_counting_qubits, marked_states)

    print(f"\nSearch space size: 2^{n_search_qubits} = {2**n_search_qubits}")
    print(f"Marked states: {marked_states}")
    print(f"Actual solution count: {len(marked_states)}")
    print(f"Counting qubits: {n_counting_qubits}")
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
        'n_search_qubits': n_search_qubits,
        'n_counting_qubits': n_counting_qubits,
        'marked_states': marked_states,
        'actual_count': len(marked_states),
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze quantum counting results."""
    print("\n" + "=" * 60)
    print("QUANTUM COUNTING RESULTS")
    print("=" * 60)

    n_search = results['n_search_qubits']
    n_counting = results['n_counting_qubits']
    actual_count = results['actual_count']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Search space: 2^{n_search} = {2**n_search}")
    print(f"Actual solutions: {actual_count}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    estimates = []
    for bitstring, count in sorted_counts[:10]:
        est = estimate_count(bitstring, n_counting, n_search)
        percentage = count / shots * 100
        estimates.append((est, count))
        print(f"  {bitstring} -> estimated count: {est}: {count} ({percentage:.1f}%)")

    # Most common estimate
    most_common = sorted_counts[0][0]
    best_estimate = estimate_count(most_common, n_counting, n_search)

    print(f"\nCounting result:")
    print(f"  Actual count: {actual_count}")
    print(f"  Best estimate: {best_estimate}")
    print(f"  Error: {abs(best_estimate - actual_count)}")

    if best_estimate == actual_count:
        print(f"\n✓ Success! Correctly counted {actual_count} solution(s).")
    else:
        print(f"\n✗ Estimate differs from actual (hardware noise or precision limit).")

    print(f"\nQuantum advantage:")
    print(f"  Quantum counting: O(√N) queries to count M solutions")
    print(f"  Classical counting: O(N) queries needed")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Quantum Counting on IBM Quantum hardware...")
        print("\nQuantum counting combines Grover's algorithm with QPE to")
        print("count the number of solutions to a search problem.\n")

        # Configuration
        n_search_qubits = 2  # Search space = 2^2 = 4
        n_counting_qubits = 3  # Precision for counting
        marked_states = [3]  # Mark state |11⟩ (1 solution)

        results = run_quantum_counting(n_search_qubits, n_counting_qubits, marked_states, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
