import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_superdense_coding_circuit(message):
    """
    Create a superdense coding circuit to send 2 classical bits using 1 qubit.

    Superdense coding allows Alice to send 2 classical bits to Bob by
    transmitting only 1 qubit, using a pre-shared entangled Bell pair.

    Protocol:
    1. Alice and Bob share an entangled Bell pair |Φ+⟩ = (|00⟩ + |11⟩)/√2
    2. Alice encodes 2 classical bits by applying operations to her qubit:
       - 00: I (identity) → |Φ+⟩
       - 01: X           → |Ψ+⟩
       - 10: Z           → |Φ-⟩
       - 11: ZX          → |Ψ-⟩
    3. Alice sends her qubit to Bob
    4. Bob performs Bell measurement to decode the 2 bits

    Args:
        message: 2-bit string to send ('00', '01', '10', or '11')

    Returns:
        QuantumCircuit implementing superdense coding
    """
    if len(message) != 2 or not all(b in '01' for b in message):
        raise ValueError("Message must be a 2-bit string: '00', '01', '10', or '11'")

    qc = QuantumCircuit(2, 2)

    # Step 1: Create entangled Bell pair |Φ+⟩ = (|00⟩ + |11⟩)/√2
    # In practice, this would be prepared beforehand and shared between Alice and Bob
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()  # Bell pair created

    # Step 2: Alice encodes the message on her qubit (qubit 0)
    # The encoding maps messages to Bell states:
    #   00 → |Φ+⟩ = (|00⟩ + |11⟩)/√2  (apply I)
    #   01 → |Ψ+⟩ = (|01⟩ + |10⟩)/√2  (apply X)
    #   10 → |Φ-⟩ = (|00⟩ - |11⟩)/√2  (apply Z)
    #   11 → |Ψ-⟩ = (|01⟩ - |10⟩)/√2  (apply ZX)

    if message[1] == '1':  # Second bit controls X gate
        qc.x(0)
    if message[0] == '1':  # First bit controls Z gate
        qc.z(0)

    qc.barrier()  # Encoding done

    # Step 3: Alice sends her qubit to Bob (implicit in the circuit)

    # Step 4: Bob performs Bell measurement (reverse of Bell state creation)
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()  # Bell measurement done

    # Measure both qubits to recover the 2-bit message
    qc.measure([0, 1], [0, 1])

    return qc


def run_superdense_coding(message='11', shots=1024):
    """
    Run superdense coding on IBM Quantum hardware.

    Args:
        message: 2-bit message to send ('00', '01', '10', or '11')
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
    qc = create_superdense_coding_circuit(message)

    print(f"\nMessage to send: '{message}'")
    print("Protocol: Alice sends 2 classical bits using 1 qubit + shared entanglement")
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
        'message': message,
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze superdense coding results."""
    print("\n" + "=" * 60)
    print("SUPERDENSE CODING RESULTS")
    print("=" * 60)

    message = results['message']
    counts = results['counts']
    shots = results['shots']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Message sent: '{message}'")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts:
        percentage = count / shots * 100
        match = "✓" if bitstring == message else ""
        print(f"  '{bitstring}': {count} ({percentage:.1f}%) {match}")

    # Calculate success rate
    correct_count = counts.get(message, 0)
    success_rate = correct_count / shots * 100

    print(f"\nDecoding accuracy:")
    print(f"  Sent message: '{message}'")
    print(f"  Most common received: '{sorted_counts[0][0]}'")
    print(f"  Correct decodings: {correct_count}/{shots} ({success_rate:.1f}%)")

    if sorted_counts[0][0] == message:
        print(f"\n✓ Success! Bob correctly decoded '{message}'.")
    else:
        print(f"\n✗ Most common result '{sorted_counts[0][0]}' differs from sent message '{message}'.")
        print("  This is due to hardware noise.")

    # Explain the protocol
    print(f"\nSuperdense coding explanation:")
    print("  1. Alice and Bob share entangled Bell pair |Φ+⟩")
    print("  2. Alice encodes 2 bits by applying gates to her qubit:")
    print("     '00' → I (identity)")
    print("     '01' → X (bit flip)")
    print("     '10' → Z (phase flip)")
    print("     '11' → ZX (both)")
    print("  3. Alice sends her 1 qubit to Bob")
    print("  4. Bob performs Bell measurement to decode 2 bits")
    print("\nQuantum advantage:")
    print("  Classical: 1 bit sent → 1 bit received")
    print("  Quantum:   1 qubit sent → 2 bits received (with pre-shared entanglement)")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def run_all_messages(shots=1024):
    """Run superdense coding with all possible 2-bit messages."""
    print("Running superdense coding with all possible messages...\n")

    all_results = []
    messages = ['00', '01', '10', '11']

    for msg in messages:
        print("=" * 60)
        print(f"Testing message: '{msg}'")
        print("=" * 60)

        results = run_superdense_coding(msg, shots=shots)
        analyze_results(results)
        all_results.append(results)
        print()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nMessage → Most common result (success rate)")
    for results in all_results:
        msg = results['message']
        counts = results['counts']
        shots = results['shots']
        if counts:
            most_common = max(counts.items(), key=lambda x: x[1])[0]
            success = counts.get(msg, 0) / shots * 100
            correct = "✓" if most_common == msg else "✗"
            print(f"  '{msg}' → '{most_common}' ({success:.1f}%) {correct}")
        else:
            print(f"  '{msg}' → No data")

    return all_results


if __name__ == "__main__":
    try:
        print("Executing Superdense Coding on IBM Quantum hardware...")
        print("\nSuperdense coding allows Alice to send 2 classical bits to Bob")
        print("by transmitting only 1 qubit, using a pre-shared entangled pair.")
        print("This demonstrates quantum communication advantage.\n")

        # Configuration
        message = '11'  # 2-bit message to send: '00', '01', '10', or '11'

        results = run_superdense_coding(message, shots=1024)
        analyze_results(results)

        # Uncomment to test all messages:
        # run_all_messages(shots=1024)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
