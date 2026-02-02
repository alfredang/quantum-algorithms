import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import numpy as np

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_bb84_circuit_with_eve(alice_bits, alice_bases, eve_bases, bob_bases):
    """
    Create a BB84 circuit with Eve's intercept-resend attack.

    In this attack, Eve:
    1. Intercepts each qubit sent by Alice
    2. Measures it in a random basis
    3. Prepares a new qubit based on her measurement result
    4. Sends this new qubit to Bob

    When Eve's basis doesn't match Alice's, she disturbs the quantum state,
    introducing errors that Alice and Bob can detect.

    Args:
        alice_bits: Alice's random bits
        alice_bases: Alice's encoding bases (0=Z, 1=X)
        eve_bases: Eve's measurement bases (0=Z, 1=X)
        bob_bases: Bob's measurement bases (0=Z, 1=X)

    Returns:
        QuantumCircuit, eve_measured_bits (simulated)
    """
    n_qubits = len(alice_bits)
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Simulate Eve's measurement results
    # When Eve's basis matches Alice's basis, Eve gets the correct bit
    # When Eve's basis differs, Eve gets a random result (50/50)
    eve_measured_bits = []
    for i in range(n_qubits):
        if eve_bases[i] == alice_bases[i]:
            # Eve measures in correct basis - gets Alice's bit
            eve_measured_bits.append(alice_bits[i])
        else:
            # Eve measures in wrong basis - gets random result
            eve_measured_bits.append(np.random.randint(2))

    # Now build the circuit: Eve prepares states based on her measurements
    # (This simulates Eve's intercept-resend attack)
    for i in range(n_qubits):
        eve_bit = eve_measured_bits[i]
        eve_basis = eve_bases[i]

        # Eve prepares qubit based on her measurement result and basis
        if eve_basis == 0:  # Z-basis
            if eve_bit == 1:
                qc.x(i)
        else:  # X-basis
            if eve_bit == 0:
                qc.h(i)
            else:
                qc.x(i)
                qc.h(i)

    qc.barrier()

    # Bob's measurement
    for i in range(n_qubits):
        if bob_bases[i] == 1:  # X-basis measurement
            qc.h(i)

    qc.measure(range(n_qubits), range(n_qubits))

    return qc, eve_measured_bits


def remove_garbage(a_bases, b_bases, bits):
    """Filter bits to keep only those where bases match."""
    return [bit for i, bit in enumerate(bits) if a_bases[i] == b_bases[i]]


def calculate_qber(alice_key, bob_key):
    """Calculate Quantum Bit Error Rate."""
    if not alice_key:
        return 0.0
    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    return errors / len(alice_key)


def run_bb84_with_eavesdropping(n_bits=8, eve_present=True, seed=None):
    """
    Run BB84 protocol with optional eavesdropping on IBM Quantum hardware.

    Args:
        n_bits: Number of qubits to use
        eve_present: Whether Eve intercepts the communication
        seed: Random seed for reproducibility

    Returns:
        Dictionary with all protocol data
    """
    if seed is not None:
        np.random.seed(seed)

    # Alice's random bits and bases
    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits)

    # Bob's random measurement bases
    bob_bases = np.random.randint(2, size=n_bits)

    # Eve's random measurement bases (only used if eve_present)
    eve_bases = np.random.randint(2, size=n_bits)

    if eve_present:
        # Create circuit with Eve's intercept-resend attack
        qc, eve_measured_bits = create_bb84_circuit_with_eve(
            alice_bits, alice_bases, eve_bases, bob_bases
        )
    else:
        # Create standard BB84 circuit (no eavesdropping)
        qc = QuantumCircuit(n_bits, n_bits)

        # Alice's state preparation
        for i in range(n_bits):
            if alice_bases[i] == 0:  # Z-basis
                if alice_bits[i] == 1:
                    qc.x(i)
            else:  # X-basis
                if alice_bits[i] == 0:
                    qc.h(i)
                else:
                    qc.x(i)
                    qc.h(i)

        qc.barrier()

        # Bob's measurement
        for i in range(n_bits):
            if bob_bases[i] == 1:
                qc.h(i)

        qc.measure(range(n_bits), range(n_bits))
        eve_measured_bits = None

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    # Get least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_bits)
    print(f"Using backend: {backend.name}")

    # Transpile and run
    transpiled_qc = transpile(qc, backend, optimization_level=1)
    print(f"Transpiled circuit depth: {transpiled_qc.depth()}")

    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled_qc], shots=1)
    print(f"Job submitted: {job.job_id()}")
    print("Waiting for results...")

    result = job.result()

    # Extract Bob's measurement results
    pub_result = result[0]
    bob_measured_bits = None

    for attr in dir(pub_result.data):
        if not attr.startswith('_'):
            try:
                data_obj = getattr(pub_result.data, attr)
                if hasattr(data_obj, 'get_counts'):
                    counts = data_obj.get_counts()
                    if counts:
                        # Get the bitstring and convert to list of bits
                        bitstring = list(counts.keys())[0]
                        bitstring = bitstring.replace(' ', '')
                        # Qiskit returns bits in reverse order
                        bob_measured_bits = [int(b) for b in bitstring[::-1]]
                        break
            except:
                pass

    if bob_measured_bits is None:
        bob_measured_bits = [0] * n_bits

    # Generate sifted keys
    alice_key = remove_garbage(alice_bases, bob_bases, list(alice_bits))
    bob_key = remove_garbage(alice_bases, bob_bases, bob_measured_bits)

    return {
        'n_bits': n_bits,
        'eve_present': eve_present,
        'alice_bits': list(alice_bits),
        'alice_bases': list(alice_bases),
        'bob_bases': list(bob_bases),
        'eve_bases': list(eve_bases) if eve_present else None,
        'eve_measured_bits': eve_measured_bits,
        'bob_measured_bits': bob_measured_bits,
        'alice_key': alice_key,
        'bob_key': bob_key,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc
    }


def analyze_results(results):
    """Analyze BB84 results and detect eavesdropping."""
    print("\n" + "=" * 70)
    if results['eve_present']:
        print("BB84 QUANTUM KEY DISTRIBUTION - WITH EAVESDROPPING")
    else:
        print("BB84 QUANTUM KEY DISTRIBUTION - NO EAVESDROPPING")
    print("=" * 70)

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Number of qubits: {results['n_bits']}")

    # Display protocol data
    print("\n--- Protocol Data ---")
    print(f"Alice's bits:   {results['alice_bits']}")
    print(f"Alice's bases:  {results['alice_bases']}  (0=Z, 1=X)")
    print(f"Bob's bases:    {results['bob_bases']}  (0=Z, 1=X)")

    if results['eve_present']:
        print(f"Eve's bases:    {results['eve_bases']}  (0=Z, 1=X)")
        print(f"Eve's results:  {results['eve_measured_bits']}")

    print(f"Bob's results:  {results['bob_measured_bits']}")

    # Basis matching
    matching_positions = [i for i in range(results['n_bits'])
                         if results['alice_bases'][i] == results['bob_bases'][i]]
    print(f"\nMatching basis positions: {matching_positions}")
    print(f"Sifted key length: {len(results['alice_key'])} bits")

    # Sifted keys
    print("\n--- Sifted Keys ---")
    print(f"Alice's key: {results['alice_key']}")
    print(f"Bob's key:   {results['bob_key']}")

    # Calculate QBER
    qber = calculate_qber(results['alice_key'], results['bob_key'])

    print("\n--- Eavesdropping Detection ---")
    print(f"Quantum Bit Error Rate (QBER): {qber:.1%}")

    # Theoretical QBER thresholds
    # - No eavesdropping: QBER ~ 0% (only hardware noise)
    # - Full intercept-resend: QBER ~ 25%
    # - Security threshold: QBER < 11%

    if qber == 0:
        print("QBER = 0%: Perfect key agreement!")
    elif qber < 0.11:
        print("QBER < 11%: Within secure threshold")
    elif qber < 0.20:
        print("QBER 11-20%: Suspicious - possible eavesdropping")
    else:
        print("QBER >= 20%: High error rate - likely eavesdropping detected!")

    if results['eve_present']:
        # Analyze Eve's interference
        eve_wrong_basis = sum(1 for i in range(results['n_bits'])
                             if results['eve_bases'][i] != results['alice_bases'][i])
        print(f"\nEve's analysis:")
        print(f"  Eve measured in wrong basis: {eve_wrong_basis}/{results['n_bits']} times")
        print(f"  Expected QBER from Eve: ~{eve_wrong_basis * 0.5 / results['n_bits'] * 100:.0f}%")
        print(f"  (Each wrong-basis measurement has 50% chance of causing error)")

    # Error positions
    errors = [(i, results['alice_key'][i], results['bob_key'][i])
              for i in range(len(results['alice_key']))
              if results['alice_key'][i] != results['bob_key'][i]]

    if errors:
        print(f"\nError positions in sifted key:")
        for pos, alice_bit, bob_bit in errors:
            print(f"  Position {pos}: Alice={alice_bit}, Bob={bob_bit}")

    # Security decision
    print("\n--- Security Decision ---")
    SECURITY_THRESHOLD = 0.11

    if qber <= SECURITY_THRESHOLD:
        print(f"QBER ({qber:.1%}) <= threshold ({SECURITY_THRESHOLD:.0%})")
        print("Decision: SECURE - Key can be used (after privacy amplification)")
        if results['eve_present']:
            print("Note: Eve was present but didn't introduce enough errors to detect")
    else:
        print(f"QBER ({qber:.1%}) > threshold ({SECURITY_THRESHOLD:.0%})")
        print("Decision: ABORT - Eavesdropping suspected, discard key!")

    # Protocol explanation
    print("\n--- How Eavesdropping Detection Works ---")
    print("1. Alice sends qubits in random bases (Z or X)")
    print("2. Eve intercepts and measures in random bases")
    print("3. Eve's measurement collapses the quantum state")
    print("4. When Eve's basis differs from Alice's:")
    print("   - Eve gets random result (50% wrong)")
    print("   - Eve prepares qubit in wrong state")
    print("   - Bob may measure different value than Alice sent")
    print("5. Expected QBER with full eavesdropping: ~25%")
    print("   (50% basis mismatch x 50% error = 25%)")
    print("6. If QBER > 11%, abort the protocol!")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


def compare_with_without_eve(n_bits=8, seed=42):
    """Run BB84 both with and without Eve to compare QBER."""
    print("=" * 70)
    print("COMPARING BB84: WITH vs WITHOUT EAVESDROPPING")
    print("=" * 70)

    print("\n[1/2] Running BB84 WITHOUT Eve...")
    results_no_eve = run_bb84_with_eavesdropping(n_bits, eve_present=False, seed=seed)
    qber_no_eve = calculate_qber(results_no_eve['alice_key'], results_no_eve['bob_key'])

    print("\n[2/2] Running BB84 WITH Eve...")
    results_with_eve = run_bb84_with_eavesdropping(n_bits, eve_present=True, seed=seed)
    qber_with_eve = calculate_qber(results_with_eve['alice_key'], results_with_eve['bob_key'])

    # Summary comparison
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"\nWithout Eve:")
    print(f"  QBER: {qber_no_eve:.1%}")
    print(f"  Alice's key: {results_no_eve['alice_key']}")
    print(f"  Bob's key:   {results_no_eve['bob_key']}")

    print(f"\nWith Eve (intercept-resend attack):")
    print(f"  QBER: {qber_with_eve:.1%}")
    print(f"  Alice's key: {results_with_eve['alice_key']}")
    print(f"  Bob's key:   {results_with_eve['bob_key']}")

    print("\nConclusion:")
    if qber_with_eve > qber_no_eve:
        print(f"  Eve's presence increased QBER by {(qber_with_eve - qber_no_eve)*100:.1f} percentage points")
        print("  Eavesdropping is detectable through increased error rate!")
    else:
        print("  Hardware noise dominated - try with more qubits for clearer results")

    return results_no_eve, results_with_eve


if __name__ == "__main__":
    try:
        print("Executing BB84 with Eavesdropping Detection on IBM Quantum hardware...")
        print("\nBB84 with Eavesdropping demonstrates how quantum mechanics")
        print("enables detection of eavesdroppers in key distribution.")
        print("\nEve's intercept-resend attack:")
        print("  1. Eve intercepts qubits sent from Alice to Bob")
        print("  2. Eve measures each qubit in a random basis")
        print("  3. Eve prepares new qubits based on her results")
        print("  4. Eve sends these new qubits to Bob")
        print("\nThis attack introduces ~25% QBER (Quantum Bit Error Rate)")
        print("because Eve measures in the wrong basis 50% of the time.\n")

        # Configuration
        n_bits = 8  # Number of qubits
        eve_present = True  # Set to False for comparison

        results = run_bb84_with_eavesdropping(n_bits, eve_present=eve_present, seed=42)
        analyze_results(results)

        # Uncomment to compare with and without Eve:
        # compare_with_without_eve(n_bits=8, seed=42)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
