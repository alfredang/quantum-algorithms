import os
import math
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def qft_rotations(circuit, n):
    """
    Apply QFT rotations to the first n qubits in the circuit.

    For each qubit j, apply:
    1. Hadamard gate
    2. Controlled rotations from qubits j+1, j+2, ..., n-1

    Args:
        circuit: QuantumCircuit to modify
        n: Number of qubits to apply QFT to
    """
    if n == 0:
        return circuit

    n -= 1
    circuit.h(n)

    for qubit in range(n):
        # Controlled rotation by 2π/2^(n-qubit+1)
        k = n - qubit + 1
        circuit.cp(2 * math.pi / (2 ** k), qubit, n)

    # Recursive call for remaining qubits
    qft_rotations(circuit, n)


def swap_registers(circuit, n):
    """
    Swap qubits to reverse the order (required for standard QFT output).

    Args:
        circuit: QuantumCircuit to modify
        n: Number of qubits
    """
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)


def create_qft_circuit(n_qubits, swap=True):
    """
    Create a Quantum Fourier Transform circuit.

    The QFT transforms |j⟩ → (1/√N) Σ_k exp(2πijk/N) |k⟩

    This is the quantum analog of the discrete Fourier transform and is
    a key component of many quantum algorithms including:
    - Shor's factoring algorithm
    - Quantum phase estimation
    - Quantum simulation

    Args:
        n_qubits: Number of qubits
        swap: Whether to include final swap gates (standard QFT requires swaps)

    Returns:
        QuantumCircuit implementing QFT
    """
    qc = QuantumCircuit(n_qubits, name=f"QFT_{n_qubits}")

    qft_rotations(qc, n_qubits)

    if swap:
        swap_registers(qc, n_qubits)

    return qc


def create_inverse_qft_circuit(n_qubits, swap=True):
    """
    Create an inverse Quantum Fourier Transform circuit.

    The inverse QFT is simply the adjoint (conjugate transpose) of the QFT.

    Args:
        n_qubits: Number of qubits
        swap: Whether to include swap gates

    Returns:
        QuantumCircuit implementing inverse QFT
    """
    qft = create_qft_circuit(n_qubits, swap)
    inverse_qft = qft.inverse()
    inverse_qft.name = f"QFT†_{n_qubits}"
    return inverse_qft


def create_qft_demo_circuit(n_qubits, input_state=None):
    """
    Create a demonstration circuit that applies QFT to an input state
    and measures the result.

    Args:
        n_qubits: Number of qubits
        input_state: Integer representing the input state (default: 0)

    Returns:
        QuantumCircuit for QFT demonstration
    """
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Prepare input state
    if input_state is not None and input_state > 0:
        # Convert integer to binary and apply X gates
        for i in range(n_qubits):
            if (input_state >> i) & 1:
                qc.x(i)
        qc.barrier(label=f"|{input_state}⟩")

    # Apply QFT
    qft = create_qft_circuit(n_qubits)
    qc.compose(qft, inplace=True)

    qc.barrier(label="QFT applied")

    # Measure all qubits
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def create_qft_inverse_test_circuit(n_qubits, input_state=None):
    """
    Create a circuit that applies QFT followed by inverse QFT.
    This should return the original state (identity operation).

    Args:
        n_qubits: Number of qubits
        input_state: Integer representing the input state

    Returns:
        QuantumCircuit for QFT-inverse test
    """
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Prepare input state
    if input_state is not None and input_state > 0:
        for i in range(n_qubits):
            if (input_state >> i) & 1:
                qc.x(i)
        qc.barrier(label=f"|{input_state}⟩")

    # Apply QFT
    qft = create_qft_circuit(n_qubits)
    qc.compose(qft, inplace=True)
    qc.barrier(label="QFT")

    # Apply inverse QFT
    inv_qft = create_inverse_qft_circuit(n_qubits)
    qc.compose(inv_qft, inplace=True)
    qc.barrier(label="QFT†")

    # Measure
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def run_qft(n_qubits, input_state=None, test_inverse=False, shots=1024):
    """
    Run the Quantum Fourier Transform on IBM Quantum hardware.

    Args:
        n_qubits: Number of qubits
        input_state: Input state as integer (e.g., 5 for |101⟩)
        test_inverse: If True, apply QFT then inverse QFT (should return input)
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
    print(f"Using backend: {backend.name}")

    # Create circuit
    if test_inverse:
        qc = create_qft_inverse_test_circuit(n_qubits, input_state)
        mode = "QFT + inverse QFT (identity test)"
    else:
        qc = create_qft_demo_circuit(n_qubits, input_state)
        mode = "QFT only"

    input_str = format(input_state if input_state else 0, f'0{n_qubits}b')

    print(f"\nMode: {mode}")
    print(f"Number of qubits: {n_qubits}")
    print(f"Input state: |{input_str}⟩ = |{input_state if input_state else 0}⟩")
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
        'input_state': input_state if input_state else 0,
        'test_inverse': test_inverse,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze QFT results."""
    print("\n" + "=" * 60)
    print("QUANTUM FOURIER TRANSFORM RESULTS")
    print("=" * 60)

    n_qubits = results['n_qubits']
    input_state = results['input_state']
    test_inverse = results['test_inverse']
    counts = results['counts']
    shots = results['shots']

    input_str = format(input_state, f'0{n_qubits}b')

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Number of qubits: {n_qubits}")
    print(f"Input state: |{input_str}⟩")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        percentage = count / shots * 100
        state_int = int(bitstring, 2)
        print(f"  |{bitstring}⟩ = |{state_int}⟩: {count} ({percentage:.1f}%)")
    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    if test_inverse:
        # For QFT + inverse QFT, we expect to get the input state back
        expected_output = input_str
        correct_count = counts.get(expected_output, 0)
        success_rate = correct_count / shots * 100

        print(f"\nIdentity test (QFT followed by QFT†):")
        print(f"  Expected output: |{expected_output}⟩")
        print(f"  Correct measurements: {correct_count}/{shots} ({success_rate:.1f}%)")

        most_common = sorted_counts[0][0]
        if most_common == expected_output:
            print(f"\n✓ Success! QFT · QFT† = Identity verified.")
        else:
            print(f"\n✗ Most common result |{most_common}⟩ differs from expected |{expected_output}⟩")
            print("  This is due to hardware noise.")
    else:
        # For QFT only, explain the expected output distribution
        print(f"\nQFT output analysis:")
        N = 2 ** n_qubits

        if input_state == 0:
            print("  Input |0⟩: QFT produces uniform superposition over all states.")
            print(f"  Expected: ~{100/N:.1f}% probability for each of {N} states.")
        else:
            print(f"  Input |{input_state}⟩: QFT produces superposition with phase-dependent amplitudes.")
            print("  The output encodes frequency information about the input.")

        # Calculate how uniform the distribution is
        expected_uniform = shots / N
        variance = sum((c - expected_uniform) ** 2 for c in counts.values()) / len(counts)
        std_dev = math.sqrt(variance)
        print(f"\n  Distribution uniformity:")
        print(f"    Expected per state: {expected_uniform:.1f}")
        print(f"    Standard deviation: {std_dev:.1f}")

    # Show QFT properties
    print(f"\nQFT properties for {n_qubits} qubits:")
    print(f"  Transform size: {2**n_qubits}")
    print(f"  Gate count: O(n²) = O({n_qubits**2})")
    print(f"  Classical FFT: O(n·2ⁿ) = O({n_qubits * 2**n_qubits})")
    print(f"  Exponential speedup for phase estimation!")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_qft_comparison(n_qubits=3, shots=1024):
    """
    Run QFT with different input states for comparison.

    Args:
        n_qubits: Number of qubits
        shots: Number of shots
    """
    print("Running QFT with different input states...\n")

    states_to_test = [0, 1, 2 ** (n_qubits - 1)]  # |0⟩, |1⟩, |100...⟩

    all_results = []
    for state in states_to_test:
        print("=" * 60)
        print(f"Testing input state: |{format(state, f'0{n_qubits}b')}⟩ = |{state}⟩")
        print("=" * 60)

        results = run_qft(n_qubits, input_state=state, test_inverse=False, shots=shots)
        analyze_results(results)
        all_results.append(results)
        print()

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Quantum Fourier Transform on IBM Quantum hardware...")
        print("\nThe Quantum Fourier Transform (QFT) is the quantum analog of the")
        print("discrete Fourier transform. It's a key component of:")
        print("  • Shor's factoring algorithm")
        print("  • Quantum phase estimation")
        print("  • Many quantum simulation algorithms")
        print("\nQFT provides EXPONENTIAL speedup over classical FFT for certain tasks.\n")

        # Configuration
        n_qubits = 5  # Number of qubits
        input_state = 0  # Input state (0 = |00000⟩)
        test_inverse = True  # If True, apply QFT then inverse (should return input)

        results = run_qft(n_qubits, input_state, test_inverse, shots=1024)
        analyze_results(results)

        # Uncomment to test with different inputs:
        # run_qft_comparison(n_qubits=3, shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
