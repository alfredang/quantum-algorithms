import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_oracle(oracle_type):
    """
    Create an oracle circuit for the Deutsch algorithm.

    The oracle implements f:{0,1}→{0,1} using the transformation:
    |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

    Args:
        oracle_type: One of 'constant_0', 'constant_1', 'balanced_identity', 'balanced_negation'

    Returns:
        QuantumCircuit implementing the oracle
    """
    oracle = QuantumCircuit(2, name=f"U_f({oracle_type})")

    if oracle_type == 'constant_0':
        # f(x) = 0: Do nothing (y ⊕ 0 = y)
        pass
    elif oracle_type == 'constant_1':
        # f(x) = 1: Flip the target qubit (y ⊕ 1 = NOT y)
        oracle.x(1)
    elif oracle_type == 'balanced_identity':
        # f(x) = x: CNOT with control on input, target on output
        oracle.cx(0, 1)
    elif oracle_type == 'balanced_negation':
        # f(x) = NOT x: CNOT then flip
        oracle.cx(0, 1)
        oracle.x(1)
    else:
        raise ValueError(f"Unknown oracle type: {oracle_type}")

    return oracle


def create_deutsch_circuit(oracle_type):
    """
    Create the complete Deutsch algorithm circuit.

    The Deutsch algorithm determines if f:{0,1}→{0,1} is constant or balanced
    using only ONE query to f, whereas classical algorithms need TWO queries.

    Circuit:
    |0⟩ ─H─┤      ├─H─ Measure → 0 if constant, 1 if balanced
           │  Uf  │
    |1⟩ ─H─┤      ├───

    Args:
        oracle_type: Type of oracle to use

    Returns:
        QuantumCircuit for Deutsch algorithm
    """
    qc = QuantumCircuit(2, 1)

    # Step 1: Initialize |0⟩|1⟩
    qc.x(1)  # Second qubit to |1⟩

    qc.barrier()

    # Step 2: Apply Hadamard to both qubits
    # Creates state: |+⟩|-⟩ = 1/2(|0⟩+|1⟩)(|0⟩-|1⟩)
    qc.h(0)
    qc.h(1)

    qc.barrier()

    # Step 3: Apply the oracle
    oracle = create_oracle(oracle_type)
    qc.compose(oracle, inplace=True)

    qc.barrier()

    # Step 4: Apply Hadamard to the first qubit
    qc.h(0)

    qc.barrier()

    # Step 5: Measure the first qubit
    # Result: 0 = constant function, 1 = balanced function
    qc.measure(0, 0)

    return qc


def run_deutsch_algorithm(oracle_type, shots=1024):
    """
    Run the Deutsch algorithm on IBM Quantum hardware.

    Args:
        oracle_type: Type of oracle ('constant_0', 'constant_1', 'balanced_identity', 'balanced_negation')
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_deutsch_circuit(oracle_type)

    print(f"\nOracle type: {oracle_type}")
    print("Circuit:")
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

    # Try different register names
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
        'oracle_type': oracle_type,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Deutsch algorithm results."""
    print("\n" + "=" * 50)
    print("DEUTSCH ALGORITHM RESULTS")
    print("=" * 50)

    oracle_type = results['oracle_type']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Oracle type: {oracle_type}")
    print(f"Total shots: {shots}")

    # Determine expected result
    if oracle_type in ['constant_0', 'constant_1']:
        expected = 'constant'
        expected_measurement = '0'
    else:
        expected = 'balanced'
        expected_measurement = '1'

    print(f"\nExpected: {expected} (measurement should be {expected_measurement})")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts: {counts}")

    # Calculate success rate
    count_0 = counts.get('0', 0)
    count_1 = counts.get('1', 0)

    print(f"\n  |0⟩ (constant): {count_0} ({count_0/shots*100:.1f}%)")
    print(f"  |1⟩ (balanced): {count_1} ({count_1/shots*100:.1f}%)")

    # Determine measured result (majority vote)
    if count_0 > count_1:
        measured = 'constant'
    else:
        measured = 'balanced'

    correct_count = counts.get(expected_measurement, 0)
    success_rate = correct_count / shots * 100

    print(f"\nAlgorithm conclusion: Function is {measured.upper()}")
    print(f"Expected result: {expected.upper()}")
    print(f"Success rate: {success_rate:.1f}%")

    if measured == expected:
        print("\n✓ Correct! The quantum algorithm correctly identified the function type.")
    else:
        print("\n✗ Incorrect due to hardware noise. The majority measurement disagrees with expected.")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_all_oracles(shots=1024):
    """Run Deutsch algorithm with all four oracle types."""
    oracle_types = ['constant_0', 'constant_1', 'balanced_identity', 'balanced_negation']

    all_results = []
    for oracle_type in oracle_types:
        print(f"\n{'='*60}")
        print(f"Testing oracle: {oracle_type}")
        print('='*60)

        results = run_deutsch_algorithm(oracle_type, shots=shots)
        analyze_results(results)
        all_results.append(results)

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Deutsch Algorithm on IBM Quantum hardware...")
        print("\nThe Deutsch algorithm determines if a function f:{0,1}→{0,1}")
        print("is CONSTANT (f(0)=f(1)) or BALANCED (f(0)≠f(1)) with ONE query.")
        print("Classical algorithms require TWO queries.\n")

        # Test with one oracle type (change as needed)
        oracle_type = 'balanced_identity'  # Options: constant_0, constant_1, balanced_identity, balanced_negation

        results = run_deutsch_algorithm(oracle_type, shots=1024)
        analyze_results(results)

        # Uncomment to test all oracles:
        # run_all_oracles(shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
