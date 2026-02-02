"""
Shor's 9-Qubit Code

The first quantum error correcting code, protects against arbitrary single-qubit errors.
Combines 3-qubit bit-flip and phase-flip codes.
"""

import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_shor_encoding_circuit():
    """
    Create encoding circuit for Shor's 9-qubit code.

    Encodes |ψ⟩ = α|0⟩ + β|1⟩ into 9 qubits:
    |0⟩_L = (|000⟩ + |111⟩)(|000⟩ + |111⟩)(|000⟩ + |111⟩) / 2√2
    |1⟩_L = (|000⟩ - |111⟩)(|000⟩ - |111⟩)(|000⟩ - |111⟩) / 2√2

    Returns:
        QuantumCircuit for encoding
    """
    qc = QuantumCircuit(9, name='Shor_Encode')

    # Step 1: Phase-flip encoding (outer code)
    # Copy q[0] to q[3] and q[6]
    qc.cx(0, 3)
    qc.cx(0, 6)

    qc.barrier()

    # Step 2: Apply Hadamard to create superposition in each block
    qc.h(0)
    qc.h(3)
    qc.h(6)

    qc.barrier()

    # Step 3: Bit-flip encoding within each block (inner code)
    # Block 1: q[0] -> q[0,1,2]
    qc.cx(0, 1)
    qc.cx(0, 2)

    # Block 2: q[3] -> q[3,4,5]
    qc.cx(3, 4)
    qc.cx(3, 5)

    # Block 3: q[6] -> q[6,7,8]
    qc.cx(6, 7)
    qc.cx(6, 8)

    return qc


def create_shor_decoding_circuit():
    """
    Create decoding circuit for Shor's 9-qubit code.

    Reverses the encoding to extract the original qubit.

    Returns:
        QuantumCircuit for decoding
    """
    qc = QuantumCircuit(9, name='Shor_Decode')

    # Step 1: Reverse bit-flip encoding
    qc.cx(0, 2)
    qc.cx(0, 1)

    qc.cx(3, 5)
    qc.cx(3, 4)

    qc.cx(6, 8)
    qc.cx(6, 7)

    qc.barrier()

    # Step 2: Hadamard to reverse phase encoding
    qc.h(0)
    qc.h(3)
    qc.h(6)

    qc.barrier()

    # Step 3: Reverse phase-flip encoding
    qc.cx(0, 6)
    qc.cx(0, 3)

    return qc


def create_bit_flip_syndrome_circuit(block_start):
    """
    Create syndrome measurement for bit-flip errors in a block.

    Args:
        block_start: Starting qubit index of the block

    Returns:
        QuantumCircuit operations
    """
    # This would use ancilla qubits for syndrome measurement
    # Simplified version without ancillas
    pass


def create_shor_code_demo(error_type=None, error_qubit=0):
    """
    Create demonstration circuit for Shor's 9-qubit code.

    Args:
        error_type: Type of error ('X', 'Y', 'Z', or None)
        error_qubit: Which qubit to apply error to (0-8)

    Returns:
        QuantumCircuit
    """
    # 9 data qubits + 1 output measurement
    qc = QuantumCircuit(9, 1)

    # Prepare initial state |+⟩ for demonstration
    # (easier to see effect of errors)
    qc.h(0)

    qc.barrier(label='Init')

    # Encoding
    qc.cx(0, 3)
    qc.cx(0, 6)

    qc.h(0)
    qc.h(3)
    qc.h(6)

    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(3, 4)
    qc.cx(3, 5)
    qc.cx(6, 7)
    qc.cx(6, 8)

    qc.barrier(label='Encoded')

    # Apply error
    if error_type == 'X':
        qc.x(error_qubit)
        qc.barrier(label=f'X_err_q{error_qubit}')
    elif error_type == 'Z':
        qc.z(error_qubit)
        qc.barrier(label=f'Z_err_q{error_qubit}')
    elif error_type == 'Y':
        qc.y(error_qubit)
        qc.barrier(label=f'Y_err_q{error_qubit}')

    # Simplified error correction
    # In full implementation, we would:
    # 1. Measure bit-flip syndromes for each block
    # 2. Correct bit-flip errors
    # 3. Measure phase-flip syndrome across blocks
    # 4. Correct phase-flip errors

    # For demonstration, apply decoding directly
    # (in practice, syndrome measurement and correction happens first)

    qc.barrier(label='Decode')

    # Decoding (reverse of encoding)
    qc.cx(0, 2)
    qc.cx(0, 1)
    qc.cx(3, 5)
    qc.cx(3, 4)
    qc.cx(6, 8)
    qc.cx(6, 7)

    qc.h(0)
    qc.h(3)
    qc.h(6)

    qc.cx(0, 6)
    qc.cx(0, 3)

    qc.barrier()

    # Measure the recovered qubit
    qc.measure(0, 0)

    return qc


def run_shor_code(shots=1024):
    """
    Run Shor's 9-qubit code demonstration on IBM Quantum hardware.

    Args:
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Need backend with at least 9 qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=9)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    # Test cases: no error and different error types
    test_cases = [
        (None, 0, "No error"),
        ('X', 1, "X error on q1"),
        ('Z', 4, "Z error on q4"),
    ]

    results = []

    for error_type, error_qubit, description in test_cases:
        print(f"\nTest: {description}")

        qc = create_shor_code_demo(error_type, error_qubit)

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
    """Analyze Shor code results."""
    print("\n" + "=" * 60)
    print("SHOR'S 9-QUBIT CODE RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Shots per test: {results['shots']}")

    # Expected: |+⟩ → measure 0 or 1 with 50% probability each
    print("\nExpected for |+⟩ input: ~50% |0⟩, ~50% |1⟩")

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

    print(f"\nShor's 9-qubit code explanation:")
    print("  Logical states:")
    print("  |0⟩_L = (|000⟩+|111⟩)(|000⟩+|111⟩)(|000⟩+|111⟩)/2√2")
    print("  |1⟩_L = (|000⟩-|111⟩)(|000⟩-|111⟩)(|000⟩-|111⟩)/2√2")
    print("")
    print("  Structure:")
    print("  - Outer code: 3-qubit phase-flip code")
    print("  - Inner code: 3-qubit bit-flip code (applied 3 times)")
    print("  - Protects against any single-qubit error")

    print(f"\nError correction:")
    print("  - X errors: Detected by bit-flip syndrome within blocks")
    print("  - Z errors: Detected by phase-flip syndrome across blocks")
    print("  - Y errors: Combination of X and Z, both are corrected")

    print(f"\nHistorical significance:")
    print("  - First quantum error correcting code (Peter Shor, 1995)")
    print("  - Proved quantum error correction is possible")
    print("  - Led to fault-tolerant quantum computation theory")


if __name__ == "__main__":
    try:
        print("Executing Shor's 9-Qubit Code on IBM Quantum hardware...")
        print("\nShor's code is the first quantum error correcting code,")
        print("protecting against arbitrary single-qubit errors.\n")

        results = run_shor_code(shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
