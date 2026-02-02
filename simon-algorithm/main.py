import os
import numpy as np
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_simon_oracle(secret_string):
    """
    Create an oracle for Simon's algorithm.

    The oracle implements f(x) such that f(x) = f(y) iff x ⊕ y ∈ {0, s}
    where s is the secret string.

    For implementation, we use: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩
    where f(x) = x if x < x⊕s, else f(x) = x⊕s

    A simpler approach: copy x to output, then XOR with s based on a control bit.

    Args:
        secret_string: The hidden binary string s (e.g., "10110")

    Returns:
        QuantumCircuit implementing the oracle
    """
    n = len(secret_string)
    oracle = QuantumCircuit(2 * n, name=f"U_s={secret_string}")

    # First, copy input register to output register
    # |x⟩|0⟩ → |x⟩|x⟩
    for i in range(n):
        oracle.cx(i, n + i)

    # If s is not all zeros, XOR output with s when a specific input bit is 1
    if '1' in secret_string:
        # Find the first 1 in s to use as control
        control_bit = secret_string.index('1')

        # For each position where s has a 1, XOR the output with s
        # This ensures f(x) = f(x⊕s)
        for i, bit in enumerate(secret_string):
            if bit == '1':
                oracle.cx(control_bit, n + i)

    return oracle


def create_simon_circuit(secret_string):
    """
    Create the complete Simon's algorithm circuit.

    Simon's algorithm finds the hidden string s where f(x) = f(y) iff x ⊕ y ∈ {0, s}.
    This provides EXPONENTIAL speedup over classical algorithms.

    Circuit structure:
    |0⟩^⊗n ─H⊗n─┤      ├─H⊗n─ Measure
                │  Uf  │
    |0⟩^⊗n ────┤      ├───── (not measured)

    Each measurement yields a string y where y · s = 0 (mod 2).
    After n-1 linearly independent measurements, we can solve for s.

    Args:
        secret_string: The hidden binary string to find

    Returns:
        QuantumCircuit for Simon's algorithm
    """
    n = len(secret_string)

    # n input qubits + n output qubits, n classical bits for measurement
    qc = QuantumCircuit(2 * n, n)

    # Step 1: Apply Hadamard to input register
    for i in range(n):
        qc.h(i)

    qc.barrier(label="H⊗n")

    # Step 2: Apply the oracle
    oracle = create_simon_oracle(secret_string)
    qc.compose(oracle, inplace=True)

    qc.barrier(label="Oracle")

    # Step 3: Apply Hadamard to input register again
    for i in range(n):
        qc.h(i)

    qc.barrier(label="H⊗n")

    # Step 4: Measure input register only
    # Each measurement gives y where y · s = 0 (mod 2)
    qc.measure(range(n), range(n))

    return qc


def dot_product_mod2(a, b):
    """Compute dot product of two binary strings modulo 2."""
    return sum(int(x) * int(y) for x, y in zip(a, b)) % 2


def solve_linear_system(equations, n):
    """
    Solve the system of linear equations over GF(2) to find the secret string s.

    Each equation is of the form: y · s = 0 (mod 2)

    Args:
        equations: List of measurement results (binary strings)
        n: Length of the secret string

    Returns:
        The secret string s, or "0"*n if s is trivial
    """
    # Convert equations to matrix form
    matrix = []
    for eq in equations:
        if eq != '0' * n:  # Skip trivial equations
            row = [int(b) for b in eq]
            matrix.append(row)

    if not matrix:
        return '0' * n

    # Gaussian elimination over GF(2)
    matrix = np.array(matrix, dtype=int)
    num_rows, num_cols = matrix.shape

    # Row reduction
    pivot_row = 0
    for col in range(num_cols):
        # Find pivot
        found = False
        for row in range(pivot_row, num_rows):
            if matrix[row, col] == 1:
                found = True
                # Swap rows
                matrix[[pivot_row, row]] = matrix[[row, pivot_row]]
                break

        if not found:
            continue

        # Eliminate other rows
        for row in range(num_rows):
            if row != pivot_row and matrix[row, col] == 1:
                matrix[row] = (matrix[row] + matrix[pivot_row]) % 2

        pivot_row += 1
        if pivot_row >= num_rows:
            break

    # Find free variables and construct solution
    # The secret s must satisfy y · s = 0 for all y in the equations
    # Try all possible solutions and find non-trivial one
    for candidate in range(1, 2 ** n):
        s_candidate = format(candidate, f'0{n}b')
        valid = True
        for eq in equations:
            if eq != '0' * n and dot_product_mod2(eq, s_candidate) != 0:
                valid = False
                break
        if valid:
            return s_candidate

    return '0' * n


def run_simon(secret_string, shots=1024):
    """
    Run Simon's algorithm on IBM Quantum hardware.

    Args:
        secret_string: The hidden binary string to find (e.g., "10110")
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    n = len(secret_string)

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend with enough qubits (need 2n qubits)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2 * n)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_simon_circuit(secret_string)

    print(f"\nSecret string to find: {secret_string}")
    print(f"Number of qubits: {2 * n} ({n} input + {n} output)")
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
    """Analyze Simon's algorithm results."""
    print("\n" + "=" * 60)
    print("SIMON'S ALGORITHM RESULTS")
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

    print(f"\nMeasurement counts (all outcomes satisfy y · s = 0):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    valid_equations = []
    for bitstring, count in sorted_counts[:15]:
        percentage = count / shots * 100
        # Check if y · s = 0 (mod 2)
        dot = dot_product_mod2(bitstring, secret_string)
        valid = "✓" if dot == 0 else "✗"
        print(f"  {bitstring}: {count} ({percentage:.1f}%) y·s={dot} {valid}")
        if dot == 0:
            valid_equations.append(bitstring)

    if len(counts) > 15:
        print(f"  ... and {len(counts) - 15} more outcomes")

    # Count valid equations (y · s = 0)
    valid_count = sum(count for bitstring, count in counts.items()
                      if dot_product_mod2(bitstring, secret_string) == 0)
    valid_rate = valid_count / shots * 100

    print(f"\nEquation validity:")
    print(f"  Measurements satisfying y · s = 0: {valid_count}/{shots} ({valid_rate:.1f}%)")
    print(f"  Expected: 100% (hardware noise causes deviations)")

    # Try to recover the secret string from equations
    print(f"\nAttempting to recover secret string from measurements...")
    equations = list(counts.keys())
    recovered_s = solve_linear_system(equations, n)

    print(f"  Actual secret:    {secret_string}")
    print(f"  Recovered secret: {recovered_s}")

    if recovered_s == secret_string:
        print(f"\n✓ Success! Correctly recovered secret string '{secret_string}'.")
    elif recovered_s == '0' * n and secret_string == '0' * n:
        print(f"\n✓ Success! Correctly identified trivial case (s = 0).")
    else:
        print(f"\n✗ Recovery mismatch. This may be due to hardware noise.")
        print("  With perfect measurements, Simon's algorithm always finds s.")

    # Quantum advantage
    print(f"\nQuantum advantage:")
    print(f"  Quantum queries needed: O(n) = O({n})")
    print(f"  Classical queries needed: O(2^(n/2)) = O({2**(n//2)})")
    print(f"  Speedup: EXPONENTIAL")

    print(f"\nAlgorithm explanation:")
    print(f"  Each measurement y satisfies y · s = 0 (mod 2)")
    print(f"  After ~n measurements, solve linear system to find s")
    print(f"  Classical algorithms must query f(x) exponentially many times")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_multiple_secrets(secrets, shots=1024):
    """Run Simon's algorithm with multiple secret strings."""
    print("Running Simon's algorithm with multiple secret strings...\n")

    all_results = []
    for secret in secrets:
        print("=" * 60)
        print(f"Testing secret string: {secret}")
        print("=" * 60)

        results = run_simon(secret, shots=shots)
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
        equations = list(counts.keys()) if counts else []
        recovered = solve_linear_system(equations, len(secret)) if equations else "N/A"
        correct = "✓" if recovered == secret else "✗"
        print(f"  Secret: {secret} → Recovered: {recovered} {correct}")

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Simon's Algorithm on IBM Quantum hardware...")
        print("\nSimon's algorithm finds a hidden string s where")
        print("f(x) = f(y) if and only if x ⊕ y ∈ {0, s}")
        print("\nThis provides EXPONENTIAL speedup over classical algorithms:")
        print("  Quantum: O(n) queries")
        print("  Classical: O(2^(n/2)) queries\n")

        # Configuration
        secret_string = "11001"  # The hidden string to find (5 bits = 10 qubits total)

        results = run_simon(secret_string, shots=1024)
        analyze_results(results)

        # Uncomment to test multiple secrets:
        # run_multiple_secrets(["101", "1101", "10011"], shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
