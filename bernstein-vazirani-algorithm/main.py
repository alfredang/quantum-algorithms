import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_bv_oracle(secret_string):
    """
    Create an oracle for the Bernstein-Vazirani algorithm.

    The oracle computes f(x) = s · x (mod 2), where s is the secret string.
    This is implemented as: |x⟩|y⟩ → |x⟩|y ⊕ (s · x)⟩

    Args:
        secret_string: The hidden binary string s (e.g., "10110")

    Returns:
        QuantumCircuit implementing the oracle
    """
    n = len(secret_string)
    oracle = QuantumCircuit(n + 1, name=f"U_s={secret_string}")

    # Apply CNOT from qubit i to ancilla for each position where s[i] = 1
    # Note: secret_string[0] corresponds to the leftmost (most significant) bit
    for i, bit in enumerate(secret_string):
        if bit == '1':
            oracle.cx(i, n)

    return oracle


def create_bernstein_vazirani_circuit(secret_string):
    """
    Create the complete Bernstein-Vazirani algorithm circuit.

    The Bernstein-Vazirani algorithm finds the hidden string s in f(x) = s · x (mod 2)
    using only ONE query to f.

    Classical algorithms require n queries (one per bit of s).

    Circuit:
    |0⟩ ─H─┤      ├─H─ Measure → s[0]
    |0⟩ ─H─┤      ├─H─ Measure → s[1]
    ...    │  Uf  │    ...
    |0⟩ ─H─┤      ├─H─ Measure → s[n-1]
    |1⟩ ─H─┤      ├───

    Args:
        secret_string: The hidden binary string to find

    Returns:
        QuantumCircuit for Bernstein-Vazirani algorithm
    """
    n = len(secret_string)

    # n input qubits + 1 ancilla qubit, n classical bits for measurement
    qc = QuantumCircuit(n + 1, n)

    # Step 1: Initialize ancilla to |1⟩
    qc.x(n)

    qc.barrier()

    # Step 2: Apply Hadamard to all qubits
    for i in range(n + 1):
        qc.h(i)

    qc.barrier()

    # Step 3: Apply the oracle
    oracle = create_bv_oracle(secret_string)
    qc.compose(oracle, inplace=True)

    qc.barrier()

    # Step 4: Apply Hadamard to input qubits (not ancilla)
    for i in range(n):
        qc.h(i)

    qc.barrier()

    # Step 5: Measure input qubits
    # The measurement result directly reveals the secret string s
    qc.measure(range(n), range(n))

    return qc


def run_bernstein_vazirani(secret_string, shots=1024):
    """
    Run the Bernstein-Vazirani algorithm on IBM Quantum hardware.

    Args:
        secret_string: The hidden binary string to find (e.g., "10110")
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    n = len(secret_string)

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend with enough qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n + 1)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_bernstein_vazirani_circuit(secret_string)

    print(f"\nSecret string to find: {secret_string}")
    print(f"Number of qubits: {n + 1} ({n} input + 1 ancilla)")
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
        'secret_string': secret_string,
        'n_qubits': n,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Bernstein-Vazirani algorithm results."""
    print("\n" + "=" * 60)
    print("BERNSTEIN-VAZIRANI ALGORITHM RESULTS")
    print("=" * 60)

    secret_string = results['secret_string']
    n = results['n_qubits']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Secret string: {secret_string}")
    print(f"String length: {n} bits")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        percentage = count / shots * 100
        match = "✓" if bitstring == secret_string else ""
        print(f"  {bitstring}: {count} ({percentage:.1f}%) {match}")
    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    # Find the most common measurement
    most_common = sorted_counts[0][0]
    most_common_count = sorted_counts[0][1]

    # Check if we found the correct secret string
    correct_count = counts.get(secret_string, 0)
    success_rate = correct_count / shots * 100

    print(f"\nExpected secret string: {secret_string}")
    print(f"Most measured string:   {most_common} ({most_common_count/shots*100:.1f}%)")
    print(f"Correct measurements:   {correct_count}/{shots} ({success_rate:.1f}%)")

    # Classical comparison
    print(f"\nQuantum advantage:")
    print(f"  Quantum queries needed: 1")
    print(f"  Classical queries needed: {n}")
    print(f"  Speedup factor: {n}x")

    if most_common == secret_string:
        print(f"\n✓ Success! Found secret string '{secret_string}' with {success_rate:.1f}% accuracy.")
    else:
        print(f"\n✗ Most common result '{most_common}' differs from secret '{secret_string}'.")
        print("  This is due to hardware noise. The correct answer had the highest probability in theory.")

        # Calculate hamming distance
        hamming = sum(a != b for a, b in zip(most_common, secret_string))
        print(f"  Hamming distance from correct answer: {hamming}")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_multiple_secrets(secrets, shots=1024):
    """Run Bernstein-Vazirani with multiple secret strings."""
    print("Running Bernstein-Vazirani with multiple secret strings...\n")

    all_results = []
    for secret in secrets:
        print("=" * 60)
        print(f"Testing secret string: {secret}")
        print("=" * 60)

        results = run_bernstein_vazirani(secret, shots=shots)
        analyze_results(results)
        all_results.append(results)
        print()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for results in all_results:
        secret = results['secret_string']
        counts = results['counts']
        most_common = max(counts.items(), key=lambda x: x[1])[0] if counts else "N/A"
        correct = "✓" if most_common == secret else "✗"
        print(f"  Secret: {secret} → Measured: {most_common} {correct}")

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Bernstein-Vazirani Algorithm on IBM Quantum hardware...")
        print("\nThe Bernstein-Vazirani algorithm finds a hidden string s")
        print("given an oracle that computes f(x) = s · x (mod 2)")
        print("using only ONE quantum query.")
        print("Classical algorithms require n queries (one per bit).\n")

        # Configuration
        secret_string = "11001"  # The hidden string to find (5 bits = 6 qubits total)

        results = run_bernstein_vazirani(secret_string, shots=1024)
        analyze_results(results)

        # Uncomment to test multiple secrets:
        # run_multiple_secrets(["101", "1101", "10011"], shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
