import os
import math
from fractions import Fraction
from dotenv import load_dotenv
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def gcd(a, b):
    """Compute greatest common divisor using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def is_coprime(a, N):
    """Check if a and N are coprime."""
    return gcd(a, N) == 1


def modular_exponentiation(a, power, N):
    """Compute a^power mod N efficiently."""
    result = 1
    a = a % N
    while power > 0:
        if power & 1:
            result = (result * a) % N
        power >>= 1
        a = (a * a) % N
    return result


def create_qft_circuit(n_qubits):
    """Create QFT circuit (used in phase estimation)."""
    qc = QuantumCircuit(n_qubits, name="QFT")

    for i in range(n_qubits - 1, -1, -1):
        qc.h(i)
        for j in range(i - 1, -1, -1):
            k = i - j + 1
            qc.cp(2 * math.pi / (2 ** k), j, i)

    # Swap qubits
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - i - 1)

    return qc


def create_inverse_qft_circuit(n_qubits):
    """Create inverse QFT circuit."""
    qft = create_qft_circuit(n_qubits)
    return qft.inverse()


def create_controlled_modular_multiplication(a, N):
    """
    Create controlled modular multiplication gate: |x⟩ → |ax mod N⟩

    For factoring 15, we implement specific controlled multiplications.
    This is a simplified version for demonstration.
    """
    # For N=15 and small a values, we use precomputed circuits
    # In a full implementation, this would use more sophisticated techniques

    if N == 15:
        if a == 7:
            # 7 mod 15 multiplication
            # Uses 4 work qubits for the number being multiplied
            qc = QuantumCircuit(4, name=f"U_{a}")
            qc.swap(0, 1)
            qc.swap(1, 2)
            qc.swap(2, 3)
            return qc
        elif a == 11:
            qc = QuantumCircuit(4, name=f"U_{a}")
            qc.swap(0, 3)
            qc.swap(1, 2)
            return qc
        elif a == 13:
            qc = QuantumCircuit(4, name=f"U_{a}")
            qc.swap(0, 1)
            qc.swap(2, 3)
            return qc
        elif a == 4:
            qc = QuantumCircuit(4, name=f"U_{a}")
            qc.swap(0, 2)
            qc.swap(1, 3)
            return qc
        elif a == 2:
            qc = QuantumCircuit(4, name=f"U_{a}")
            qc.swap(0, 1)
            qc.swap(1, 2)
            qc.swap(2, 3)
            return qc

    # Default: identity (for unsupported cases)
    return QuantumCircuit(4, name=f"U_{a}")


def create_shor_circuit(N, a, n_count):
    """
    Create Shor's algorithm circuit for factoring N using base a.

    The circuit performs quantum phase estimation to find the period r
    of the function f(x) = a^x mod N.

    Args:
        N: Number to factor
        a: Base for modular exponentiation (must be coprime to N)
        n_count: Number of counting qubits (determines precision)

    Returns:
        QuantumCircuit for Shor's algorithm
    """
    # Need n_count counting qubits + enough qubits to represent N
    n_work = 4  # For N=15, we need 4 qubits to represent numbers 0-15

    # Create registers
    counting_qubits = QuantumRegister(n_count, 'count')
    work_qubits = QuantumRegister(n_work, 'work')
    classical_bits = ClassicalRegister(n_count, 'meas')

    qc = QuantumCircuit(counting_qubits, work_qubits, classical_bits)

    # Initialize work register to |1⟩ (since a^0 mod N = 1)
    qc.x(work_qubits[0])

    qc.barrier(label="Init |1⟩")

    # Apply Hadamard to all counting qubits
    for q in range(n_count):
        qc.h(counting_qubits[q])

    qc.barrier(label="Hadamard")

    # Apply controlled-U^(2^j) operations
    # U|y⟩ = |ay mod N⟩
    for q in range(n_count):
        power = 2 ** q
        # Compute a^(2^q) mod N
        a_power = modular_exponentiation(a, power, N)

        # Apply controlled modular multiplication
        U = create_controlled_modular_multiplication(a_power, N)
        controlled_U = U.control(1, label=f"U^{power}")
        qc.compose(controlled_U, [counting_qubits[q]] + list(work_qubits), inplace=True)

    qc.barrier(label="Controlled-U")

    # Apply inverse QFT to counting register
    inv_qft = create_inverse_qft_circuit(n_count)
    qc.compose(inv_qft, counting_qubits, inplace=True)

    qc.barrier(label="QFT†")

    # Measure counting qubits
    qc.measure(counting_qubits, classical_bits)

    return qc


def analyze_shor_measurement(measurement, n_count, N, a):
    """
    Analyze the measurement result from Shor's algorithm to find factors.

    Args:
        measurement: Measured value from counting register
        n_count: Number of counting qubits
        N: Number being factored
        a: Base used

    Returns:
        Tuple of (period_candidate, factors) or (None, None) if no factor found
    """
    # Convert measurement to phase
    phase = measurement / (2 ** n_count)

    if phase == 0:
        return None, None

    # Use continued fractions to find period
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator

    if r == 0 or r % 2 != 0:
        return r, None

    # Try to find factors
    guess1 = gcd(modular_exponentiation(a, r // 2, N) - 1, N)
    guess2 = gcd(modular_exponentiation(a, r // 2, N) + 1, N)

    factors = []
    for guess in [guess1, guess2]:
        if 1 < guess < N:
            factors.append(guess)

    return r, factors if factors else None


def run_shor(N, a=None, n_count=4, shots=1024):
    """
    Run Shor's algorithm on IBM Quantum hardware.

    Args:
        N: Number to factor
        a: Base for modular exponentiation (random if None)
        n_count: Number of counting qubits
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Validate N
    if N < 3:
        raise ValueError("N must be >= 3")
    if N % 2 == 0:
        print(f"N={N} is even. Factor: 2 and {N//2}")
        return {'factors': [2, N // 2], 'trivial': True}

    # Check if N is a prime power
    for k in range(2, int(math.log2(N)) + 1):
        root = round(N ** (1 / k))
        if root ** k == N:
            print(f"N={N} is a prime power: {root}^{k}")
            return {'factors': [root], 'trivial': True}

    # Choose a if not provided
    if a is None:
        # For N=15, good choices are 2, 4, 7, 8, 11, 13, 14
        a = 7  # Default for demonstration

    # Check if a is coprime to N
    g = gcd(a, N)
    if g > 1:
        print(f"Lucky! gcd({a}, {N}) = {g} is a factor!")
        return {'factors': [g, N // g], 'trivial': True}

    print(f"Factoring N={N} using a={a}")
    print(f"Counting qubits: {n_count}")

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend (need n_count + 4 qubits for N=15)
    total_qubits = n_count + 4
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=total_qubits)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_shor_circuit(N, a, n_count)

    print(f"\nTotal qubits: {total_qubits}")
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
        'N': N,
        'a': a,
        'n_count': n_count,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Shor's algorithm results."""
    if results.get('trivial'):
        print(f"\n✓ Trivial factorization: {results['factors']}")
        return

    print("\n" + "=" * 60)
    print("SHOR'S ALGORITHM RESULTS")
    print("=" * 60)

    N = results['N']
    a = results['a']
    n_count = results['n_count']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Number to factor: N = {N}")
    print(f"Base: a = {a}")
    print(f"Counting qubits: {n_count}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    found_factors = set()
    period_candidates = {}

    for bitstring, count in sorted_counts[:10]:
        measurement = int(bitstring, 2)
        percentage = count / shots * 100

        # Analyze this measurement
        r, factors = analyze_shor_measurement(measurement, n_count, N, a)

        factor_str = ""
        if factors:
            for f in factors:
                found_factors.add(f)
                found_factors.add(N // f)
            factor_str = f" → factors: {factors}"
        elif r:
            period_candidates[r] = period_candidates.get(r, 0) + count

        print(f"  |{bitstring}⟩ = {measurement}: {count} ({percentage:.1f}%)" +
              (f" [r={r}]" if r else "") + factor_str)

    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    # Summary
    print(f"\nPeriod candidates found: {list(period_candidates.keys())}")

    if found_factors:
        found_factors.discard(1)
        found_factors.discard(N)
        if found_factors:
            factors_list = sorted(found_factors)
            print(f"\n✓ SUCCESS! Factors of {N}: {factors_list}")
            # Verify
            if len(factors_list) >= 2:
                print(f"  Verification: {factors_list[0]} × {factors_list[1]} = {factors_list[0] * factors_list[1]}")
        else:
            print(f"\n✗ No non-trivial factors found in top measurements.")
            print("  This may be due to hardware noise or insufficient shots.")
    else:
        print(f"\n✗ No factors found. Try:")
        print("  - More shots")
        print("  - Different base 'a'")
        print("  - More counting qubits")

    # Classical verification of the period
    print(f"\nClassical verification for a={a}, N={N}:")
    for i in range(1, 20):
        if modular_exponentiation(a, i, N) == 1:
            print(f"  Period r = {i} (since {a}^{i} ≡ 1 mod {N})")
            if i % 2 == 0:
                x = modular_exponentiation(a, i // 2, N)
                f1, f2 = gcd(x - 1, N), gcd(x + 1, N)
                print(f"  gcd({a}^{i//2} - 1, {N}) = gcd({x-1}, {N}) = {f1}")
                print(f"  gcd({a}^{i//2} + 1, {N}) = gcd({x+1}, {N}) = {f2}")
            break

    # Explain quantum advantage
    print(f"\nQuantum advantage:")
    print(f"  Classical factoring: O(exp(n^(1/3))) - exponential")
    print(f"  Shor's algorithm: O(n³) - polynomial")
    print(f"  For N={N} ({N.bit_length()} bits), quantum provides exponential speedup!")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Shor's Algorithm on IBM Quantum hardware...")
        print("\nShor's algorithm factors integers in polynomial time,")
        print("breaking RSA encryption. This demonstrates quantum supremacy")
        print("for a problem with major practical implications.\n")

        # Configuration
        N = 15  # Number to factor (15 = 3 × 5)
        a = 7   # Base for modular exponentiation (coprime to N)
        n_count = 4  # Counting qubits (determines precision)

        print(f"Attempting to factor N = {N}")
        print(f"Using base a = {a}")
        print(f"Expected factors: 3 and 5\n")

        results = run_shor(N, a, n_count, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
