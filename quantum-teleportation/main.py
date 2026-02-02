import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_teleportation_circuit(state_params=None):
    """
    Create a quantum teleportation circuit.

    Quantum teleportation transfers a quantum state from Alice's qubit (q0)
    to Bob's qubit (q2) using an entangled Bell pair and classical communication.

    Args:
        state_params: Tuple (theta, phi) to prepare initial state.
                     If None, teleports |1⟩ state.

    Returns:
        QuantumCircuit for teleportation
    """
    # Quantum registers
    qr = QuantumRegister(3, 'q')
    # Classical registers for Bell measurement and final verification
    cr_bell = ClassicalRegister(2, 'bell')  # Alice's Bell measurement results
    cr_result = ClassicalRegister(1, 'result')  # Bob's final measurement

    qc = QuantumCircuit(qr, cr_bell, cr_result)

    # Step 1: Prepare the state to teleport on q0 (Alice's qubit)
    if state_params:
        theta, phi = state_params
        qc.ry(theta, qr[0])
        qc.rz(phi, qr[0])
    else:
        # Default: teleport |1⟩ state
        qc.x(qr[0])

    qc.barrier(label="State prepared")

    # Step 2: Create entangled Bell pair between q1 (Alice) and q2 (Bob)
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])

    qc.barrier(label="Bell pair created")

    # Step 3: Alice performs Bell measurement on q0 and q1
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])

    qc.barrier(label="Bell measurement")

    # Measure Alice's qubits
    qc.measure(qr[0], cr_bell[0])
    qc.measure(qr[1], cr_bell[1])

    qc.barrier(label="Classical comm")

    # Step 4: Bob applies corrections based on Alice's measurement results
    # Using dynamic circuits with classical conditionals
    with qc.if_test((cr_bell[1], 1)):
        qc.x(qr[2])
    with qc.if_test((cr_bell[0], 1)):
        qc.z(qr[2])

    qc.barrier(label="Corrections applied")

    # Step 5: Measure Bob's qubit to verify teleportation
    qc.measure(qr[2], cr_result[0])

    return qc


def create_teleportation_circuit_deferred(state_params=None):
    """
    Create teleportation circuit with deferred measurement (for backends without dynamic circuits).

    This version doesn't use mid-circuit measurement and classical conditionals.
    Instead, it measures all qubits at the end and post-processes results.
    """
    qc = QuantumCircuit(3, 3)

    # Step 1: Prepare state to teleport on q0
    if state_params:
        theta, phi = state_params
        qc.ry(theta, 0)
        qc.rz(phi, 0)
    else:
        qc.x(0)  # Teleport |1⟩

    qc.barrier()

    # Step 2: Create Bell pair (q1, q2)
    qc.h(1)
    qc.cx(1, 2)

    qc.barrier()

    # Step 3: Bell measurement basis rotation
    qc.cx(0, 1)
    qc.h(0)

    qc.barrier()

    # Measure all qubits
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


def run_teleportation(shots=1024, use_dynamic_circuits=True):
    """
    Run quantum teleportation on IBM Quantum hardware.

    Args:
        shots: Number of circuit executions
        use_dynamic_circuits: If True, use real-time classical conditionals

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend with enough qubits
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Using backend: {backend.name}")

    # Check if backend supports dynamic circuits
    supports_dynamic = getattr(backend, 'supports_dynamic_circuits', lambda: False)()

    if use_dynamic_circuits and supports_dynamic:
        print("Using dynamic circuit with mid-circuit measurement")
        qc = create_teleportation_circuit()
    else:
        print("Using deferred measurement circuit")
        qc = create_teleportation_circuit_deferred()
        use_dynamic_circuits = False

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
    counts = pub_result.data.meas.get_counts() if hasattr(pub_result.data, 'meas') else {}

    # Try different register names
    if not counts:
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
        'counts': counts,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots,
        'use_dynamic_circuits': use_dynamic_circuits
    }


def analyze_results(results):
    """Analyze teleportation results."""
    print("\n" + "="*50)
    print("QUANTUM TELEPORTATION RESULTS")
    print("="*50)

    counts = results['counts']
    shots = results['shots']
    use_dynamic = results['use_dynamic_circuits']

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Total shots: {shots}")

    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nMeasurement counts: {counts}")

    if use_dynamic:
        # For dynamic circuits: result register shows Bob's qubit
        success_count = 0
        for bitstring, count in counts.items():
            # The result bit (rightmost) should be 1 (we teleported |1⟩)
            if bitstring[-1] == '1':
                success_count += count

        success_rate = success_count / shots * 100
        print(f"\nTeleportation success rate: {success_rate:.1f}%")
        print("(Expected: ~100% for perfect teleportation of |1⟩)")
    else:
        # For deferred measurement: analyze correlations
        # Format: q2 q1 q0 (Bob, Alice's Bell measurement)
        print("\nAnalyzing deferred measurement results:")
        print("Format: q2(Bob) q1 q0(Alice's Bell measurement)")

        correct_count = 0
        for bitstring, count in counts.items():
            bits = bitstring.replace(' ', '')
            if len(bits) >= 3:
                _q0, q1, q2 = int(bits[-1]), int(bits[-2]), int(bits[-3])
                # After corrections: Bob should have |1⟩
                # Correction logic: X if q1=1, Z if q0=1
                # For |1⟩ state, Z correction doesn't affect measurement outcome
                corrected = q2 ^ q1  # X correction only
                if corrected == 1:
                    correct_count += count

        success_rate = correct_count / shots * 100
        print(f"\nTeleportation success rate (with post-selection): {success_rate:.1f}%")
        print("(Expected: ~100% for perfect teleportation, lower due to noise)")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Quantum Teleportation on IBM Quantum hardware...")
        print("Teleporting state: |1⟩\n")

        results = run_teleportation(shots=1024, use_dynamic_circuits=False)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
