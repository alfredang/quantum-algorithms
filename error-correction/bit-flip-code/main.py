import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_bit_flip_code_circuit(initial_state='0', error_qubit=None):
    """
    Create the complete 3-qubit bit-flip error correction circuit.

    This simplified version measures all qubits at the end and uses
    post-processing to analyze error correction performance.

    Encodes: |0⟩ → |000⟩, |1⟩ → |111⟩

    Args:
        initial_state: '0' or '1' for the logical qubit state
        error_qubit: Which qubit to apply error to (0, 1, 2, or None for no error)

    Returns:
        QuantumCircuit for bit-flip error correction
    """
    # 3 data qubits + 2 ancilla qubits, 5 classical bits
    qc = QuantumCircuit(5, 5)

    # Step 1: Prepare initial state on qubit 0
    if initial_state == '1':
        qc.x(0)

    # Step 2: Encode |ψ⟩ → |ψψψ⟩
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()

    # Step 3: Introduce error (simulating noise)
    if error_qubit is not None and 0 <= error_qubit <= 2:
        qc.x(error_qubit)
    qc.barrier()

    # Step 4: Syndrome measurement (parity checks)
    # Ancilla 3: parity of qubits 0 and 1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # Ancilla 4: parity of qubits 1 and 2
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.barrier()

    # Step 5: Measure all qubits
    # We'll use post-processing to determine the syndrome and apply corrections
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])

    return qc


def run_bit_flip_code(initial_state='0', error_qubit=1, shots=1024):
    """
    Run the 3-qubit bit-flip code on IBM Quantum hardware.

    Args:
        initial_state: '0' or '1' for logical qubit
        error_qubit: Which qubit to apply error (0, 1, 2, or None)
        shots: Number of circuit executions

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend (need 5 qubits: 3 data + 2 ancilla)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=5)
    print(f"Using backend: {backend.name}")

    # Create circuit
    qc = create_bit_flip_code_circuit(initial_state, error_qubit)

    error_str = f"qubit {error_qubit}" if error_qubit is not None else "none"

    print(f"\nCode type: 3-qubit bit-flip code")
    print(f"Initial logical state: |{initial_state}⟩")
    print(f"Error introduced: X (bit-flip) on {error_str}")
    print(f"Expected output after correction: |{initial_state}⟩")
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
        'initial_state': initial_state,
        'error_qubit': error_qubit,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def apply_correction(data_bits, syndrome):
    """
    Apply error correction based on syndrome.

    Syndrome interpretation:
    - 00: No error
    - 01: Error on qubit 2
    - 10: Error on qubit 0
    - 11: Error on qubit 1

    Args:
        data_bits: List of 3 data qubit values [q0, q1, q2]
        syndrome: 2-bit syndrome string

    Returns:
        Corrected logical value (0 or 1)
    """
    corrected = list(data_bits)

    if syndrome == '10':
        corrected[0] = 1 - corrected[0]  # Flip qubit 0
    elif syndrome == '01':
        corrected[2] = 1 - corrected[2]  # Flip qubit 2
    elif syndrome == '11':
        corrected[1] = 1 - corrected[1]  # Flip qubit 1
    # syndrome '00' means no error

    # Decode by majority vote
    return 1 if sum(corrected) >= 2 else 0


def analyze_results(results):
    """Analyze bit-flip code results with post-processing error correction."""
    print("\n" + "=" * 60)
    print("3-QUBIT BIT-FLIP CODE RESULTS")
    print("=" * 60)

    initial_state = results['initial_state']
    error_qubit = results['error_qubit']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Initial state: |{initial_state}⟩")
    error_str = f"qubit {error_qubit}" if error_qubit is not None else "none"
    print(f"Error location: {error_str}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    expected = int(initial_state)

    # Analyze with and without error correction
    correct_without_ec = 0
    correct_with_ec = 0
    syndrome_counts = {'00': 0, '01': 0, '10': 0, '11': 0}

    print(f"\nRaw measurement results (top 10):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:10]:
        bits = bitstring.replace(' ', '')
        if len(bits) >= 5:
            # Format: q4 q3 q2 q1 q0 (ancilla1, ancilla0, data2, data1, data0)
            q0 = int(bits[-1])
            q1 = int(bits[-2])
            q2 = int(bits[-3])
            anc0 = int(bits[-4])
            anc1 = int(bits[-5])

            syndrome = f"{anc1}{anc0}"
            syndrome_counts[syndrome] = syndrome_counts.get(syndrome, 0) + count

            # Without error correction: use majority vote on data qubits
            uncorrected = 1 if (q0 + q1 + q2) >= 2 else 0

            # With error correction: apply syndrome-based correction
            corrected = apply_correction([q0, q1, q2], syndrome)

            if uncorrected == expected:
                correct_without_ec += count
            if corrected == expected:
                correct_with_ec += count

        percentage = count / shots * 100
        print(f"  {bitstring}: {count} ({percentage:.1f}%)")

    if len(counts) > 10:
        print(f"  ... and {len(counts) - 10} more outcomes")

    # Process remaining counts
    for bitstring, count in sorted_counts[10:]:
        bits = bitstring.replace(' ', '')
        if len(bits) >= 5:
            q0 = int(bits[-1])
            q1 = int(bits[-2])
            q2 = int(bits[-3])
            anc0 = int(bits[-4])
            anc1 = int(bits[-5])

            syndrome = f"{anc1}{anc0}"
            syndrome_counts[syndrome] = syndrome_counts.get(syndrome, 0) + count

            uncorrected = 1 if (q0 + q1 + q2) >= 2 else 0
            corrected = apply_correction([q0, q1, q2], syndrome)

            if uncorrected == expected:
                correct_without_ec += count
            if corrected == expected:
                correct_with_ec += count

    # Syndrome distribution
    print(f"\nSyndrome distribution:")
    syndrome_meanings = {
        '00': 'No error detected',
        '01': 'Error on qubit 2',
        '10': 'Error on qubit 0',
        '11': 'Error on qubit 1'
    }
    for syndrome in ['00', '01', '10', '11']:
        count = syndrome_counts[syndrome]
        percentage = count / shots * 100
        meaning = syndrome_meanings[syndrome]
        expected_syn = "✓" if (error_qubit is None and syndrome == '00') or \
                              (error_qubit == 0 and syndrome == '10') or \
                              (error_qubit == 1 and syndrome == '11') or \
                              (error_qubit == 2 and syndrome == '01') else ""
        print(f"  {syndrome}: {count} ({percentage:.1f}%) - {meaning} {expected_syn}")

    # Success rates
    success_without_ec = correct_without_ec / shots * 100
    success_with_ec = correct_with_ec / shots * 100

    print(f"\nError correction performance:")
    print(f"  Expected output: |{initial_state}⟩")
    print(f"  Without error correction (majority vote): {success_without_ec:.1f}%")
    print(f"  With syndrome-based correction: {success_with_ec:.1f}%")

    if error_qubit is not None:
        print(f"\n  Note: Without ANY correction, success would be 0%")
        print(f"        (the intentional error flips the state)")

    if success_with_ec > success_without_ec:
        print(f"\n✓ Syndrome-based correction improved results by {success_with_ec - success_without_ec:.1f}%")
    elif success_with_ec >= 50:
        print(f"\n✓ Error correction successful (>{success_with_ec:.0f}% accuracy)")
    else:
        print(f"\n✗ Hardware noise overwhelmed the error correction.")

    # Explanation
    print(f"\nHow bit-flip code works:")
    print("  Encoding: |0⟩ → |000⟩, |1⟩ → |111⟩")
    print("  Syndrome 00: No error → no correction")
    print("  Syndrome 01: Error on q2 → flip q2")
    print("  Syndrome 10: Error on q0 → flip q0")
    print("  Syndrome 11: Error on q1 → flip q1")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing 3-Qubit Bit-Flip Code on IBM Quantum hardware...")
        print("\nThe bit-flip code is the simplest quantum error correction code.")
        print("It protects against single bit-flip (X) errors by encoding")
        print("one logical qubit into three physical qubits:")
        print("  |0⟩ → |000⟩")
        print("  |1⟩ → |111⟩")
        print("\nSyndrome measurement identifies which qubit (if any) was flipped.\n")

        # Configuration
        initial_state = '1'  # Logical qubit state: '0' or '1'
        error_qubit = 1      # Apply error to qubit 0, 1, 2, or None for no error

        results = run_bit_flip_code(initial_state, error_qubit, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
