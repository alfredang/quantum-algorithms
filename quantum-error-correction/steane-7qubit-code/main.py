"""
Steane's 7-Qubit Code

A CSS (Calderbank-Shor-Steane) code based on the classical [7,4,3] Hamming code.
More efficient than Shor's code (7 vs 9 qubits) and allows transversal gates.
"""

import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_steane_encoding_circuit():
    """
    Create encoding circuit for Steane's 7-qubit code.

    The Steane code is a [[7,1,3]] code based on the Hamming code.
    Encodes 1 logical qubit into 7 physical qubits.

    Generator matrix for classical Hamming [7,4,3]:
    G = [1 0 0 0 0 1 1]
        [0 1 0 0 1 0 1]
        [0 0 1 0 1 1 0]
        [0 0 0 1 1 1 1]

    Logical states:
    |0⟩_L = (|0000000⟩ + |1010101⟩ + |0110011⟩ + |1100110⟩
           + |0001111⟩ + |1011010⟩ + |0111100⟩ + |1101001⟩) / √8
    |1⟩_L = X_L|0⟩_L

    Returns:
        QuantumCircuit for encoding
    """
    qc = QuantumCircuit(7, name='Steane_Encode')

    # Input is on q[0]
    # Encoding uses a sequence of CNOT and Hadamard gates

    # Step 1: Initialize ancillas in superposition
    qc.h(4)
    qc.h(5)
    qc.h(6)

    qc.barrier()

    # Step 2: CNOT gates based on parity check matrix
    # These create the code structure

    # From q[4] (controls q[0,2,4,6] for H1)
    qc.cx(4, 0)
    qc.cx(4, 2)

    # From q[5] (controls q[1,2,5,6] for H2)
    qc.cx(5, 1)
    qc.cx(5, 2)

    # From q[6] (controls q[3,4,5,6] for H3)
    qc.cx(6, 3)
    qc.cx(6, 4)
    qc.cx(6, 5)

    return qc


def create_steane_code_demo(error_type=None, error_qubit=0):
    """
    Create demonstration circuit for Steane's 7-qubit code.

    Args:
        error_type: Type of error ('X', 'Z', or None)
        error_qubit: Which qubit to apply error to (0-6)

    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(7, 1)

    # Prepare initial state (|0⟩ or |+⟩)
    # Using |0⟩ for simplicity
    # For |+⟩: qc.h(0)

    # Steane encoding
    # Initialize "check" qubits in superposition
    qc.h(4)
    qc.h(5)
    qc.h(6)

    qc.barrier(label='Init')

    # Create encoded state through CNOT network
    # Based on Hamming code structure
    qc.cx(4, 0)
    qc.cx(4, 2)
    qc.cx(5, 1)
    qc.cx(5, 2)
    qc.cx(6, 3)
    qc.cx(6, 4)
    qc.cx(6, 5)

    qc.barrier(label='Encoded')

    # Apply error if specified
    if error_type == 'X':
        qc.x(error_qubit)
        qc.barrier(label=f'X_err_q{error_qubit}')
    elif error_type == 'Z':
        qc.z(error_qubit)
        qc.barrier(label=f'Z_err_q{error_qubit}')
    elif error_type == 'Y':
        qc.y(error_qubit)
        qc.barrier(label=f'Y_err_q{error_qubit}')

    # In full implementation: syndrome measurement and correction here
    # The Steane code syndrome identifies which qubit has an error

    qc.barrier(label='Decode')

    # Decoding (reverse of encoding)
    qc.cx(6, 5)
    qc.cx(6, 4)
    qc.cx(6, 3)
    qc.cx(5, 2)
    qc.cx(5, 1)
    qc.cx(4, 2)
    qc.cx(4, 0)

    qc.h(4)
    qc.h(5)
    qc.h(6)

    qc.barrier()

    # Measure logical qubit
    qc.measure(0, 0)

    return qc


def create_steane_syndrome_circuit():
    """
    Create syndrome measurement circuit for Steane code.

    X-error syndrome uses Z-type stabilizers.
    Z-error syndrome uses X-type stabilizers.

    Returns:
        QuantumCircuit with ancilla qubits
    """
    # 7 data + 6 ancilla (3 for X syndrome, 3 for Z syndrome)
    qc = QuantumCircuit(13, 6)

    # Data qubits: 0-6
    # X-syndrome ancillas: 7-9
    # Z-syndrome ancillas: 10-12

    # Prepare ancillas
    for i in range(7, 13):
        qc.h(i)

    qc.barrier()

    # X-error syndrome (Z-type stabilizers)
    # S1 = Z0Z2Z4Z6
    qc.cz(7, 0)
    qc.cz(7, 2)
    qc.cz(7, 4)
    qc.cz(7, 6)

    # S2 = Z1Z2Z5Z6
    qc.cz(8, 1)
    qc.cz(8, 2)
    qc.cz(8, 5)
    qc.cz(8, 6)

    # S3 = Z3Z4Z5Z6
    qc.cz(9, 3)
    qc.cz(9, 4)
    qc.cz(9, 5)
    qc.cz(9, 6)

    qc.barrier()

    # Z-error syndrome (X-type stabilizers)
    # S4 = X0X2X4X6
    qc.cx(0, 10)
    qc.cx(2, 10)
    qc.cx(4, 10)
    qc.cx(6, 10)

    # S5 = X1X2X5X6
    qc.cx(1, 11)
    qc.cx(2, 11)
    qc.cx(5, 11)
    qc.cx(6, 11)

    # S6 = X3X4X5X6
    qc.cx(3, 12)
    qc.cx(4, 12)
    qc.cx(5, 12)
    qc.cx(6, 12)

    qc.barrier()

    # Measure ancillas
    for i in range(7, 13):
        qc.h(i)

    qc.measure([7, 8, 9], [0, 1, 2])  # X-syndrome
    qc.measure([10, 11, 12], [3, 4, 5])  # Z-syndrome

    return qc


def run_steane_code(shots=1024):
    """
    Run Steane's 7-qubit code demonstration on IBM Quantum hardware.

    Args:
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Need backend with at least 7 qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=7)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    # Test cases
    test_cases = [
        (None, 0, "No error"),
        ('X', 2, "X error on q2"),
        ('Z', 5, "Z error on q5"),
    ]

    results = []

    for error_type, error_qubit, description in test_cases:
        print(f"\nTest: {description}")

        qc = create_steane_code_demo(error_type, error_qubit)

        if error_type is None:
            print("Circuit (no error):")
            print(qc.draw())

        # Transpile and run
        transpiled = transpile(qc, backend, optimization_level=1)
        print(f"  Transpiled depth: {transpiled.depth()}")

        job = sampler.run([transpiled], shots=shots)
        print(f"  Job ID: {job.job_id()}")

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

        results.append({
            'description': description,
            'error_type': error_type,
            'error_qubit': error_qubit,
            'counts': counts,
            'circuit': qc
        })

    return {
        'test_results': results,
        'backend': backend.name,
        'shots': shots
    }


def analyze_results(results):
    """Analyze Steane code results."""
    print("\n" + "=" * 60)
    print("STEANE'S 7-QUBIT CODE RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Shots per test: {results['shots']}")

    print("\nExpected for |0⟩ input: ~100% |0⟩")

    for test in results['test_results']:
        print(f"\n{test['description']}:")
        counts = test['counts']
        if counts:
            total = sum(counts.values())
            for outcome, count in sorted(counts.items()):
                outcome = outcome.replace(' ', '')
                percentage = count / total * 100
                print(f"  |{outcome}⟩: {count} ({percentage:.1f}%)")
        else:
            print("  No counts available")

    print(f"\nSteane's 7-qubit code explanation:")
    print("  [[7,1,3]] CSS code based on Hamming [7,4,3] code")
    print("")
    print("  Stabilizer generators:")
    print("  X-type: X⊗X⊗X⊗X⊗I⊗I⊗I, etc.")
    print("  Z-type: Z⊗Z⊗Z⊗Z⊗I⊗I⊗I, etc.")
    print("")
    print("  Properties:")
    print("  - Encodes 1 logical qubit in 7 physical qubits")
    print("  - Distance 3: corrects any single-qubit error")
    print("  - CSS code: X and Z errors handled separately")

    print(f"\nAdvantages over Shor code:")
    print("  - Fewer qubits (7 vs 9)")
    print("  - Transversal logical gates (H, CNOT)")
    print("  - Efficient syndrome measurement")

    print(f"\nSyndrome decoding (X-errors):")
    print("  Syndrome | Error qubit")
    print("  000      | No error")
    print("  001      | q0")
    print("  010      | q1")
    print("  011      | q2")
    print("  100      | q3")
    print("  101      | q4")
    print("  110      | q5")
    print("  111      | q6")


if __name__ == "__main__":
    try:
        print("Executing Steane's 7-Qubit Code on IBM Quantum hardware...")
        print("\nThe Steane code is a CSS code that encodes 1 logical qubit")
        print("into 7 physical qubits with distance 3.\n")

        results = run_steane_code(shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
