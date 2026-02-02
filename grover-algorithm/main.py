import os
import math
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_oracle(n_qubits, marked_states):
    """
    Create an oracle that marks the target states by flipping their phase.

    The oracle implements: |x⟩ → (-1)^f(x)|x⟩
    where f(x) = 1 if x is a marked state, 0 otherwise.

    Args:
        n_qubits: Number of qubits
        marked_states: List of states to mark (as integers or binary strings)

    Returns:
        QuantumCircuit implementing the oracle
    """
    oracle = QuantumCircuit(n_qubits, name="Oracle")

    # Convert marked states to integers if they're strings
    marked_ints = []
    for state in marked_states:
        if isinstance(state, str):
            marked_ints.append(int(state, 2))
        else:
            marked_ints.append(state)

    for target in marked_ints:
        # Create a multi-controlled Z gate that flips phase of |target⟩
        # First, flip qubits where target has 0 bits
        for i in range(n_qubits):
            if not (target >> i) & 1:
                oracle.x(i)

        # Apply multi-controlled Z (implemented as H-MCX-H on last qubit)
        if n_qubits == 1:
            oracle.z(0)
        elif n_qubits == 2:
            oracle.cz(0, 1)
        else:
            # Multi-controlled Z using MCX with H gates
            oracle.h(n_qubits - 1)
            oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            oracle.h(n_qubits - 1)

        # Undo the X gates
        for i in range(n_qubits):
            if not (target >> i) & 1:
                oracle.x(i)

    return oracle


def create_diffuser(n_qubits):
    """
    Create the Grover diffusion operator (amplitude amplification).

    The diffuser implements: 2|ψ⟩⟨ψ| - I
    where |ψ⟩ is the uniform superposition state.

    This is equivalent to: H⊗n (2|0⟩⟨0| - I) H⊗n

    Args:
        n_qubits: Number of qubits

    Returns:
        QuantumCircuit implementing the diffuser
    """
    diffuser = QuantumCircuit(n_qubits, name="Diffuser")

    # Apply H gates
    for i in range(n_qubits):
        diffuser.h(i)

    # Apply X gates
    for i in range(n_qubits):
        diffuser.x(i)

    # Multi-controlled Z gate (phase flip of |0...0⟩ after X gates = |1...1⟩)
    if n_qubits == 1:
        diffuser.z(0)
    elif n_qubits == 2:
        diffuser.cz(0, 1)
    else:
        diffuser.h(n_qubits - 1)
        diffuser.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        diffuser.h(n_qubits - 1)

    # Undo X gates
    for i in range(n_qubits):
        diffuser.x(i)

    # Apply H gates
    for i in range(n_qubits):
        diffuser.h(i)

    return diffuser


def optimal_iterations(n_qubits, num_marked=1):
    """
    Calculate the optimal number of Grover iterations.

    The optimal number is approximately π/4 * √(N/M)
    where N = 2^n is the search space size and M is the number of marked items.

    Args:
        n_qubits: Number of qubits
        num_marked: Number of marked states

    Returns:
        Optimal number of iterations
    """
    N = 2 ** n_qubits
    return max(1, round(math.pi / 4 * math.sqrt(N / num_marked)))


def create_grover_circuit(n_qubits, marked_states, num_iterations=None):
    """
    Create the complete Grover's algorithm circuit.

    Grover's algorithm searches an unsorted database of N items for marked items
    using O(√N) queries, compared to O(N) classical queries.

    Circuit structure:
    |0⟩^⊗n ─H⊗n─┤ Oracle ├─┤ Diffuser ├─ ... ─ Measure

    Args:
        n_qubits: Number of qubits (search space = 2^n)
        marked_states: List of target states to find
        num_iterations: Number of Grover iterations (None = optimal)

    Returns:
        QuantumCircuit for Grover's algorithm
    """
    if num_iterations is None:
        num_iterations = optimal_iterations(n_qubits, len(marked_states))

    qc = QuantumCircuit(n_qubits, n_qubits)

    # Step 1: Create uniform superposition
    for i in range(n_qubits):
        qc.h(i)

    qc.barrier()

    # Step 2: Apply Grover iterations
    oracle = create_oracle(n_qubits, marked_states)
    diffuser = create_diffuser(n_qubits)

    for iteration in range(num_iterations):
        # Apply oracle
        qc.compose(oracle, inplace=True)
        qc.barrier()

        # Apply diffuser
        qc.compose(diffuser, inplace=True)

        if iteration < num_iterations - 1:
            qc.barrier()

    qc.barrier()

    # Step 3: Measure all qubits
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def run_grover(n_qubits, marked_states, num_iterations=None, shots=1024):
    """
    Run Grover's algorithm on IBM Quantum hardware.

    Args:
        n_qubits: Number of qubits
        marked_states: Target states to find (as integers or binary strings)
        num_iterations: Number of iterations (None = optimal)
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Normalize marked states to binary strings
    marked_strings = []
    for state in marked_states:
        if isinstance(state, int):
            marked_strings.append(format(state, f'0{n_qubits}b'))
        else:
            marked_strings.append(state.zfill(n_qubits))

    if num_iterations is None:
        num_iterations = optimal_iterations(n_qubits, len(marked_states))

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_grover_circuit(n_qubits, marked_states, num_iterations)

    print(f"\nSearch space size: {2**n_qubits}")
    print(f"Marked states: {marked_strings}")
    print(f"Grover iterations: {num_iterations}")
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
        'n_qubits': n_qubits,
        'marked_states': marked_strings,
        'num_iterations': num_iterations,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Grover's algorithm results."""
    print("\n" + "=" * 60)
    print("GROVER'S ALGORITHM RESULTS")
    print("=" * 60)

    n_qubits = results['n_qubits']
    marked_states = results['marked_states']
    num_iterations = results['num_iterations']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Search space: {2**n_qubits} items ({n_qubits} qubits)")
    print(f"Target states: {marked_states}")
    print(f"Grover iterations: {num_iterations}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        percentage = count / shots * 100
        is_target = "✓ TARGET" if bitstring in marked_states else ""
        print(f"  {bitstring}: {count} ({percentage:.1f}%) {is_target}")
    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    # Calculate success rate (probability of measuring a marked state)
    marked_count = sum(counts.get(state, 0) for state in marked_states)
    success_rate = marked_count / shots * 100

    # Find most common result
    most_common = sorted_counts[0][0]
    most_common_count = sorted_counts[0][1]

    print(f"\nResults summary:")
    print(f"  Most measured: {most_common} ({most_common_count/shots*100:.1f}%)")
    print(f"  Target states measured: {marked_count}/{shots} ({success_rate:.1f}%)")

    # Theoretical success probability
    N = 2 ** n_qubits
    M = len(marked_states)
    theta = math.asin(math.sqrt(M / N))
    theoretical_prob = math.sin((2 * num_iterations + 1) * theta) ** 2 * 100

    print(f"\nTheoretical success probability: {theoretical_prob:.1f}%")
    print(f"Measured success rate: {success_rate:.1f}%")

    # Quantum advantage
    classical_queries = N // 2  # Average case for classical search
    quantum_queries = num_iterations
    print(f"\nQuantum advantage:")
    print(f"  Quantum queries (Grover iterations): {quantum_queries}")
    print(f"  Classical queries (average): {classical_queries}")
    print(f"  Speedup factor: ~{classical_queries / max(1, quantum_queries):.1f}x")

    if most_common in marked_states:
        print(f"\n✓ Success! Found target state '{most_common}'.")
    else:
        print(f"\n✗ Most common result '{most_common}' is not a target state.")
        print("  This may be due to hardware noise or insufficient iterations.")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_multiple_searches(searches, shots=1024):
    """
    Run Grover's algorithm with multiple search configurations.

    Args:
        searches: List of (n_qubits, marked_states) tuples
        shots: Number of shots per search
    """
    all_results = []
    for n_qubits, marked_states in searches:
        print("=" * 60)
        print(f"Searching for {marked_states} in {2**n_qubits}-item database")
        print("=" * 60)

        results = run_grover(n_qubits, marked_states, shots=shots)
        analyze_results(results)
        all_results.append(results)
        print()

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Grover's Algorithm on IBM Quantum hardware...")
        print("\nGrover's algorithm searches an unsorted database of N items")
        print("for marked items using O(√N) queries.")
        print("Classical algorithms require O(N) queries on average.")
        print("This provides a QUADRATIC speedup.\n")

        # Configuration
        n_qubits = 5  # Search space = 2^5 = 32 items
        marked_states = ["10101"]  # Target state(s) to find (can be multiple)

        # Number of iterations (None = optimal)
        num_iterations = None

        results = run_grover(n_qubits, marked_states, num_iterations, shots=1024)
        analyze_results(results)

        # Uncomment to test multiple searches:
        # run_multiple_searches([
        #     (2, ["11"]),      # 4 items, find "11"
        #     (3, ["101"]),     # 8 items, find "101"
        #     (3, ["010", "110"]),  # 8 items, find 2 targets
        # ], shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
