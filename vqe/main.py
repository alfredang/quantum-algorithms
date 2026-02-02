"""
Variational Quantum Eigensolver (VQE)

A hybrid quantum-classical algorithm to find the ground state energy of a Hamiltonian.
Most widely used algorithm on NISQ devices for quantum chemistry applications.
"""

import os
import math
import numpy as np
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def create_ansatz(n_qubits, params, layers=1):
    """
    Create a parameterized quantum circuit (ansatz) for VQE.

    Uses a hardware-efficient ansatz with Ry rotations and CNOT entanglement.

    Args:
        n_qubits: Number of qubits
        params: List of rotation angles
        layers: Number of variational layers

    Returns:
        QuantumCircuit with parameterized gates
    """
    qc = QuantumCircuit(n_qubits)
    param_idx = 0

    for layer in range(layers):
        # Rotation layer
        for i in range(n_qubits):
            qc.ry(params[param_idx], i)
            param_idx += 1

        # Entanglement layer
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)

        if layer < layers - 1:
            qc.barrier()

    # Final rotation layer
    for i in range(n_qubits):
        qc.ry(params[param_idx], i)
        param_idx += 1

    return qc


def create_measurement_circuits(ansatz, hamiltonian_terms):
    """
    Create circuits to measure each term in the Hamiltonian.

    For H = Σ cᵢ Pᵢ where Pᵢ are Pauli strings,
    we need to measure in appropriate bases.

    Args:
        ansatz: The variational circuit
        hamiltonian_terms: List of (coefficient, pauli_string) tuples

    Returns:
        List of measurement circuits
    """
    circuits = []
    n_qubits = ansatz.num_qubits

    for coeff, pauli_string in hamiltonian_terms:
        qc = ansatz.copy()
        qc.add_register(ansatz.cregs[0] if ansatz.cregs else None)
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.compose(ansatz, inplace=True)

        # Change basis for measurement
        for i, pauli in enumerate(pauli_string):
            if pauli == 'X':
                qc.h(i)
            elif pauli == 'Y':
                qc.sdg(i)
                qc.h(i)
            # Z basis needs no change

        qc.measure(range(n_qubits), range(n_qubits))
        circuits.append((coeff, pauli_string, qc))

    return circuits


def compute_expectation(counts, pauli_string, shots):
    """
    Compute expectation value from measurement counts.

    Args:
        counts: Measurement counts dictionary
        pauli_string: The Pauli string being measured
        shots: Total number of shots

    Returns:
        Expectation value
    """
    expectation = 0.0

    for bitstring, count in counts.items():
        bitstring = bitstring.replace(' ', '')
        # Compute parity of relevant qubits
        parity = 0
        for i, pauli in enumerate(pauli_string):
            if pauli != 'I':
                bit_idx = len(bitstring) - 1 - i
                if bit_idx >= 0:
                    parity ^= int(bitstring[bit_idx])

        # Eigenvalue is +1 for even parity, -1 for odd
        eigenvalue = 1 - 2 * parity
        expectation += eigenvalue * count / shots

    return expectation


def run_vqe_iteration(params, n_qubits, hamiltonian, backend, sampler, shots=1024):
    """
    Run one iteration of VQE: prepare state and measure energy.

    Args:
        params: Current variational parameters
        n_qubits: Number of qubits
        hamiltonian: List of (coefficient, pauli_string) tuples
        backend: IBM Quantum backend
        sampler: Sampler primitive
        shots: Number of shots per circuit

    Returns:
        Estimated energy
    """
    # Create ansatz with current parameters
    ansatz = create_ansatz(n_qubits, params, layers=1)

    energy = 0.0

    for coeff, pauli_string in hamiltonian:
        if pauli_string == 'I' * n_qubits:
            # Identity term
            energy += coeff
            continue

        # Create measurement circuit
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.compose(ansatz, inplace=True)

        # Change basis
        for i, pauli in enumerate(pauli_string):
            if pauli == 'X':
                qc.h(i)
            elif pauli == 'Y':
                qc.sdg(i)
                qc.h(i)

        qc.measure(range(n_qubits), range(n_qubits))

        # Transpile and run
        transpiled = transpile(qc, backend, optimization_level=1)
        job = sampler.run([transpiled], shots=shots)
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

        # Compute expectation
        exp_val = compute_expectation(counts, pauli_string, shots)
        energy += coeff * exp_val

    return energy


def run_vqe(n_qubits=2, max_iterations=5, shots=1024):
    """
    Run VQE to find ground state energy of H₂ molecule (simplified).

    Args:
        n_qubits: Number of qubits
        max_iterations: Maximum optimization iterations
        shots: Number of shots per measurement

    Returns:
        Dictionary with results
    """
    # Simplified H₂ Hamiltonian in minimal basis
    # H = c₀I + c₁Z₀ + c₂Z₁ + c₃Z₀Z₁ + c₄X₀X₁ + c₅Y₀Y₁
    hamiltonian = [
        (-1.0523732, 'II'),
        (0.39793742, 'IZ'),
        (-0.39793742, 'ZI'),
        (-0.01128010, 'ZZ'),
        (0.18093119, 'XX'),
        (0.18093119, 'YY')
    ]

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    # Number of parameters: (layers + 1) * n_qubits
    n_params = 2 * n_qubits

    # Initial parameters (random)
    np.random.seed(42)
    params = np.random.uniform(0, 2 * np.pi, n_params)

    print(f"\nRunning VQE for H₂ molecule")
    print(f"Qubits: {n_qubits}")
    print(f"Parameters: {n_params}")
    print(f"Max iterations: {max_iterations}")

    # Simple gradient-free optimization (for demonstration)
    best_energy = float('inf')
    best_params = params.copy()
    energies = []

    for iteration in range(max_iterations):
        print(f"\nIteration {iteration + 1}/{max_iterations}")

        # Evaluate current parameters
        energy = run_vqe_iteration(params, n_qubits, hamiltonian, backend, sampler, shots)
        energies.append(energy)
        print(f"  Energy: {energy:.6f} Hartree")

        if energy < best_energy:
            best_energy = energy
            best_params = params.copy()

        # Simple parameter update (random perturbation for demo)
        params = best_params + 0.1 * np.random.randn(n_params)

    # Create final ansatz circuit for display
    final_ansatz = create_ansatz(n_qubits, best_params, layers=1)

    return {
        'best_energy': best_energy,
        'best_params': best_params,
        'energies': energies,
        'hamiltonian': hamiltonian,
        'n_qubits': n_qubits,
        'backend': backend.name,
        'circuit': final_ansatz,
        'shots': shots
    }


def analyze_results(results):
    """Analyze VQE results."""
    print("\n" + "=" * 60)
    print("VQE RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Qubits: {results['n_qubits']}")

    print(f"\nOptimization history:")
    for i, energy in enumerate(results['energies']):
        print(f"  Iteration {i+1}: {energy:.6f} Hartree")

    print(f"\nFinal results:")
    print(f"  Best energy: {results['best_energy']:.6f} Hartree")
    print(f"  Best parameters: {results['best_params']}")

    # Exact ground state energy of H₂ at equilibrium is about -1.137 Hartree
    exact_energy = -1.137
    error = abs(results['best_energy'] - exact_energy)
    print(f"\n  Exact H₂ ground state: {exact_energy:.6f} Hartree")
    print(f"  Error: {error:.6f} Hartree")

    print(f"\nVQE explanation:")
    print("  1. Prepare parameterized quantum state |ψ(θ)⟩")
    print("  2. Measure energy ⟨ψ(θ)|H|ψ(θ)⟩")
    print("  3. Classical optimizer updates θ to minimize energy")
    print("  4. Repeat until convergence")

    print(f"\nApplications:")
    print("  - Quantum chemistry (molecular ground states)")
    print("  - Materials science")
    print("  - Drug discovery")

    print("\nFinal ansatz circuit:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing VQE on IBM Quantum hardware...")
        print("\nVQE is a hybrid quantum-classical algorithm to find")
        print("ground state energies, widely used for quantum chemistry.\n")

        # Configuration
        n_qubits = 2
        max_iterations = 3  # Reduced for demo

        results = run_vqe(n_qubits, max_iterations, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
