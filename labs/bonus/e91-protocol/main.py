"""
E91 Protocol (Ekert 1991)

Quantum key distribution protocol based on entanglement and Bell inequality.
Security is guaranteed by the violation of Bell inequality.
"""

import os
import math
import random
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


# E91 measurement bases (angles in radians)
# Alice's bases: 0, π/8, π/4
# Bob's bases: π/8, π/4, 3π/8
ALICE_BASES = [0, math.pi/8, math.pi/4]
ALICE_LABELS = ['A1', 'A2', 'A3']

BOB_BASES = [math.pi/8, math.pi/4, 3*math.pi/8]
BOB_LABELS = ['B1', 'B2', 'B3']


def create_bell_pair():
    """
    Create a Bell pair (maximally entangled state).

    |Φ⁺⟩ = (|00⟩ + |11⟩) / √2

    Returns:
        QuantumCircuit creating Bell pair
    """
    qc = QuantumCircuit(2, name='BellPair')
    qc.h(0)
    qc.cx(0, 1)
    return qc


def create_measurement_circuit(alice_basis, bob_basis):
    """
    Create circuit for E91 measurement.

    Args:
        alice_basis: Alice's measurement angle
        bob_basis: Bob's measurement angle

    Returns:
        QuantumCircuit
    """
    qc = QuantumCircuit(2, 2)

    # Create Bell pair
    qc.h(0)
    qc.cx(0, 1)

    qc.barrier()

    # Alice measures qubit 0 in rotated basis
    # Rotation Ry(-2θ) before Z measurement = measurement in θ direction
    qc.ry(-2 * alice_basis, 0)

    # Bob measures qubit 1 in rotated basis
    qc.ry(-2 * bob_basis, 1)

    qc.barrier()

    # Measure both qubits
    qc.measure([0, 1], [0, 1])

    return qc


def compute_correlation(counts, shots):
    """
    Compute correlation coefficient E(a,b) from measurement counts.

    E(a,b) = P(same) - P(different)
           = (N(00) + N(11) - N(01) - N(10)) / N_total

    Args:
        counts: Measurement counts
        shots: Total shots

    Returns:
        Correlation coefficient
    """
    n_same = 0
    n_diff = 0

    for bitstring, count in counts.items():
        bitstring = bitstring.replace(' ', '')
        if len(bitstring) >= 2:
            alice_bit = bitstring[-1]  # Qiskit convention
            bob_bit = bitstring[-2]

            if alice_bit == bob_bit:
                n_same += count
            else:
                n_diff += count

    correlation = (n_same - n_diff) / shots
    return correlation


def compute_chsh_value(E_ab, E_ab_prime, E_a_prime_b, E_a_prime_b_prime):
    """
    Compute CHSH value S.

    S = E(A1,B1) - E(A1,B3) + E(A3,B1) + E(A3,B3)

    Classical bound: |S| ≤ 2
    Quantum bound: |S| ≤ 2√2 ≈ 2.83

    Args:
        E_ab, E_ab_prime, E_a_prime_b, E_a_prime_b_prime: Correlation values

    Returns:
        CHSH value S
    """
    return E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime


def run_e91_protocol(n_rounds=5, shots_per_measurement=1024):
    """
    Run E91 quantum key distribution protocol.

    Args:
        n_rounds: Number of key generation rounds
        shots_per_measurement: Shots per basis combination

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    # First: Test Bell inequality to verify quantum correlations
    print("\n=== Bell Inequality Test ===")

    # Measure correlations for CHSH test
    # S = E(A1,B1) - E(A1,B3) + E(A3,B1) + E(A3,B3)
    chsh_measurements = [
        (0, 0, 'E(A1,B1)'),  # Alice A1 (0), Bob B1 (π/8)
        (0, 2, 'E(A1,B3)'),  # Alice A1 (0), Bob B3 (3π/8)
        (2, 0, 'E(A3,B1)'),  # Alice A3 (π/4), Bob B1 (π/8)
        (2, 2, 'E(A3,B3)'),  # Alice A3 (π/4), Bob B3 (3π/8)
    ]

    correlations = {}

    for alice_idx, bob_idx, label in chsh_measurements:
        alice_angle = ALICE_BASES[alice_idx]
        bob_angle = BOB_BASES[bob_idx]

        qc = create_measurement_circuit(alice_angle, bob_angle)

        transpiled = transpile(qc, backend, optimization_level=1)
        job = sampler.run([transpiled], shots=shots_per_measurement)
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

        E = compute_correlation(counts, shots_per_measurement)
        correlations[label] = E
        print(f"  {label}: {E:.4f}")

    # Compute CHSH value
    S = correlations['E(A1,B1)'] - correlations['E(A1,B3)'] + correlations['E(A3,B1)'] + correlations['E(A3,B3)']
    print(f"\nCHSH value S = {S:.4f}")
    print(f"Classical bound: |S| ≤ 2")
    print(f"Quantum bound: |S| ≤ 2√2 ≈ 2.83")

    if abs(S) > 2:
        print("✓ Bell inequality violated! Quantum correlations confirmed.")
    else:
        print("✗ No violation (may be due to noise)")

    # Key generation phase
    print("\n=== Key Generation ===")

    # For key generation, Alice and Bob use matching bases
    # A2 = B1 = π/8 and A3 = B2 = π/4
    key_bases = [
        (1, 0, 'A2=B1'),  # Alice A2, Bob B1 (both π/8)
        (2, 1, 'A3=B2'),  # Alice A3, Bob B2 (both π/4)
    ]

    alice_key = []
    bob_key = []

    for round_num in range(n_rounds):
        # Randomly choose matching basis pair
        basis_choice = random.randint(0, 1)
        alice_idx, bob_idx, basis_name = key_bases[basis_choice]

        alice_angle = ALICE_BASES[alice_idx]
        bob_angle = BOB_BASES[bob_idx]

        qc = create_measurement_circuit(alice_angle, bob_angle)
        transpiled = transpile(qc, backend, optimization_level=1)
        job = sampler.run([transpiled], shots=1)
        result = job.result()

        # Get single measurement
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

        if counts:
            bitstring = list(counts.keys())[0].replace(' ', '')
            alice_bit = int(bitstring[-1])
            bob_bit = int(bitstring[-2])

            alice_key.append(alice_bit)
            bob_key.append(bob_bit)

            print(f"  Round {round_num+1}: Basis={basis_name}, Alice={alice_bit}, Bob={bob_bit}")

    # Check key agreement
    matching = sum(1 for a, b in zip(alice_key, bob_key) if a == b)
    agreement_rate = matching / len(alice_key) * 100 if alice_key else 0

    return {
        'correlations': correlations,
        'chsh_value': S,
        'bell_violated': abs(S) > 2,
        'alice_key': alice_key,
        'bob_key': bob_key,
        'key_agreement_rate': agreement_rate,
        'backend': backend.name,
        'shots': shots_per_measurement
    }


def analyze_results(results):
    """Analyze E91 protocol results."""
    print("\n" + "=" * 60)
    print("E91 PROTOCOL RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")

    print(f"\n--- Bell Inequality Test ---")
    for label, E in results['correlations'].items():
        print(f"  {label} = {E:.4f}")

    S = results['chsh_value']
    print(f"\nCHSH value S = {S:.4f}")
    if results['bell_violated']:
        print("✓ Bell inequality VIOLATED (|S| > 2)")
        print("  Quantum correlations verified - secure channel")
    else:
        print("✗ Bell inequality NOT violated")
        print("  Possible eavesdropping or excessive noise")

    print(f"\n--- Generated Key ---")
    print(f"Alice's key: {results['alice_key']}")
    print(f"Bob's key:   {results['bob_key']}")
    print(f"Key agreement: {results['key_agreement_rate']:.1f}%")

    # Due to same basis and perfect entanglement, keys should be anticorrelated
    # (When measured in same basis, Bell pair gives opposite results)

    print(f"\nE91 protocol explanation:")
    print("  1. Source creates entangled Bell pairs")
    print("  2. Alice and Bob each receive one qubit")
    print("  3. Each randomly chooses measurement basis:")
    print("     Alice: A1(0°), A2(22.5°), A3(45°)")
    print("     Bob:   B1(22.5°), B2(45°), B3(67.5°)")
    print("  4. After measurement, they publicly share basis choices")
    print("  5. Matching bases (A2=B1, A3=B2) → key generation")
    print("  6. Non-matching bases → Bell inequality test")
    print("  7. Bell violation confirms no eavesdropping")

    print(f"\nSecurity guarantee:")
    print("  - Eavesdropping disturbs entanglement")
    print("  - This reduces Bell inequality violation")
    print("  - Any interception is detectable!")

    print(f"\nAdvantages over BB84:")
    print("  - Security based on fundamental physics (Bell's theorem)")
    print("  - No need to trust the source")
    print("  - Device-independent security possible")


if __name__ == "__main__":
    try:
        print("Executing E91 Protocol on IBM Quantum hardware...")
        print("\nE91 uses entanglement and Bell inequality for")
        print("provably secure quantum key distribution.\n")

        results = run_e91_protocol(n_rounds=5, shots_per_measurement=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
