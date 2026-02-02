import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_constant_oracle(n_qubits, output_value=0):
    """
    Create a constant oracle: f(x) = constant for all x.

    Args:
        n_qubits: Number of input qubits
        output_value: 0 or 1 (the constant output)

    Returns:
        QuantumCircuit implementing the oracle
    """
    oracle = QuantumCircuit(n_qubits + 1, name=f"U_constant_{output_value}")

    if output_value == 1:
        # f(x) = 1: flip the ancilla qubit
        oracle.x(n_qubits)

    return oracle


def create_balanced_oracle(n_qubits, pattern=None):
    """
    Create a balanced oracle: f(x) = 0 for half of inputs, 1 for the other half.

    The oracle computes f(x) = x · s (inner product mod 2) for some secret string s.
    This guarantees exactly half of inputs map to 0 and half to 1.

    Args:
        n_qubits: Number of input qubits
        pattern: Binary pattern determining which qubits contribute to the inner product.
                 If None, uses all 1s (parity function).

    Returns:
        QuantumCircuit implementing the oracle
    """
    oracle = QuantumCircuit(n_qubits + 1, name="U_balanced")

    if pattern is None:
        # Default: parity of all bits (inner product with 111...1)
        pattern = [1] * n_qubits

    # Apply CNOT from each input qubit where pattern[i] = 1 to the ancilla
    for i, bit in enumerate(pattern):
        if bit == 1:
            oracle.cx(i, n_qubits)

    return oracle


def create_deutsch_jozsa_circuit(n_qubits, oracle_type, oracle_param=None):
    """
    Create the complete Deutsch-Jozsa algorithm circuit.

    The Deutsch-Jozsa algorithm determines if f:{0,1}^n → {0,1} is constant or balanced
    using only ONE query to f.

    Classical deterministic algorithms require 2^(n-1) + 1 queries in the worst case.

    Circuit:
    |0⟩ ─H─┤      ├─H─ Measure ┐
    |0⟩ ─H─┤      ├─H─ Measure ├─ All 0s = constant, otherwise = balanced
    ...    │  Uf  │    ...     │
    |0⟩ ─H─┤      ├─H─ Measure ┘
    |1⟩ ─H─┤      ├───

    Args:
        n_qubits: Number of input qubits (function domain is {0,1}^n)
        oracle_type: 'constant_0', 'constant_1', or 'balanced'
        oracle_param: For balanced oracle, the pattern determining which bits to use

    Returns:
        QuantumCircuit for Deutsch-Jozsa algorithm
    """
    # n input qubits + 1 ancilla qubit, n classical bits for measurement
    qc = QuantumCircuit(n_qubits + 1, n_qubits)

    # Step 1: Initialize ancilla to |1⟩
    qc.x(n_qubits)

    qc.barrier()

    # Step 2: Apply Hadamard to all qubits
    for i in range(n_qubits + 1):
        qc.h(i)

    qc.barrier()

    # Step 3: Apply the oracle
    if oracle_type == 'constant_0':
        oracle = create_constant_oracle(n_qubits, output_value=0)
    elif oracle_type == 'constant_1':
        oracle = create_constant_oracle(n_qubits, output_value=1)
    elif oracle_type == 'balanced':
        oracle = create_balanced_oracle(n_qubits, pattern=oracle_param)
    else:
        raise ValueError(f"Unknown oracle type: {oracle_type}")

    qc.compose(oracle, inplace=True)

    qc.barrier()

    # Step 4: Apply Hadamard to input qubits (not ancilla)
    for i in range(n_qubits):
        qc.h(i)

    qc.barrier()

    # Step 5: Measure input qubits
    # Result: all 0s = constant function, any 1s = balanced function
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def run_deutsch_jozsa(n_qubits, oracle_type, oracle_param=None, shots=1024):
    """
    Run the Deutsch-Jozsa algorithm on IBM Quantum hardware.

    Args:
        n_qubits: Number of input qubits
        oracle_type: 'constant_0', 'constant_1', or 'balanced'
        oracle_param: For balanced oracle, the pattern for inner product
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend with enough qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits + 1)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_deutsch_jozsa_circuit(n_qubits, oracle_type, oracle_param)

    print(f"\nNumber of input qubits: {n_qubits}")
    print(f"Oracle type: {oracle_type}")
    if oracle_type == 'balanced' and oracle_param:
        print(f"Balanced pattern: {oracle_param}")
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
        'oracle_type': oracle_type,
        'oracle_param': oracle_param,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Deutsch-Jozsa algorithm results."""
    print("\n" + "=" * 60)
    print("DEUTSCH-JOZSA ALGORITHM RESULTS")
    print("=" * 60)

    n_qubits = results['n_qubits']
    oracle_type = results['oracle_type']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Input qubits: {n_qubits}")
    print(f"Oracle type: {oracle_type}")
    print(f"Total shots: {shots}")

    # Determine expected result
    if oracle_type in ['constant_0', 'constant_1']:
        expected = 'constant'
        expected_measurement = '0' * n_qubits
    else:
        expected = 'balanced'
        expected_measurement = 'non-zero'

    print(f"\nExpected: {expected}")
    if expected == 'constant':
        print(f"  (measurement should be {expected_measurement})")
    else:
        print(f"  (measurement should be anything except {'0' * n_qubits})")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        percentage = count / shots * 100
        print(f"  {bitstring}: {count} ({percentage:.1f}%)")
    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    # Calculate success
    all_zeros = '0' * n_qubits
    zero_count = counts.get(all_zeros, 0)
    nonzero_count = shots - zero_count

    print(f"\nSummary:")
    print(f"  All zeros ({all_zeros}): {zero_count} ({zero_count/shots*100:.1f}%)")
    print(f"  Non-zero outcomes: {nonzero_count} ({nonzero_count/shots*100:.1f}%)")

    # Determine measured result (majority)
    if zero_count > nonzero_count:
        measured = 'constant'
    else:
        measured = 'balanced'

    # Calculate success rate
    if expected == 'constant':
        success_rate = zero_count / shots * 100
    else:
        success_rate = nonzero_count / shots * 100

    print(f"\nAlgorithm conclusion: Function is {measured.upper()}")
    print(f"Expected result: {expected.upper()}")
    print(f"Success rate: {success_rate:.1f}%")

    # Classical comparison
    classical_queries = 2 ** (n_qubits - 1) + 1
    print(f"\nQuantum advantage:")
    print(f"  Quantum queries needed: 1")
    print(f"  Classical queries needed (worst case): {classical_queries}")
    print(f"  Speedup factor: {classical_queries}x")

    if measured == expected:
        print("\n✓ Correct! The quantum algorithm correctly identified the function type.")
    else:
        print("\n✗ Incorrect due to hardware noise.")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_comparison(n_qubits=5, shots=1024):
    """Run Deutsch-Jozsa with both constant and balanced oracles for comparison."""
    print("Running comparison of constant vs balanced oracles...\n")

    # Test constant oracle
    print("=" * 60)
    print("TEST 1: Constant Oracle (f(x) = 0)")
    print("=" * 60)
    results_const = run_deutsch_jozsa(n_qubits, 'constant_0', shots=shots)
    analyze_results(results_const)

    # Test balanced oracle
    print("\n" + "=" * 60)
    print("TEST 2: Balanced Oracle (f(x) = parity of x)")
    print("=" * 60)
    results_balanced = run_deutsch_jozsa(n_qubits, 'balanced', shots=shots)
    analyze_results(results_balanced)

    return [results_const, results_balanced]


if __name__ == "__main__":
    try:
        print("Executing Deutsch-Jozsa Algorithm on IBM Quantum hardware...")
        print("\nThe Deutsch-Jozsa algorithm determines if f:{0,1}^n → {0,1}")
        print("is CONSTANT (same output for all inputs) or BALANCED (0 for half, 1 for half)")
        print("using only ONE quantum query.")
        print("Classical algorithms require up to 2^(n-1)+1 queries.\n")

        # Configuration
        n_qubits = 5  # Number of input qubits (total qubits = n + 1)
        oracle_type = 'balanced'  # Options: 'constant_0', 'constant_1', 'balanced'

        # For balanced oracle, optionally specify which bits contribute
        # e.g., [1, 0, 1] means f(x) = x[0] XOR x[2]
        balanced_pattern = None  # None uses all bits (parity function)

        results = run_deutsch_jozsa(n_qubits, oracle_type, balanced_pattern, shots=1024)
        analyze_results(results)

        # Uncomment to run comparison:
        # run_comparison(n_qubits=3, shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
