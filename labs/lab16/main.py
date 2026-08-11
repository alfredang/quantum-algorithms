"""
Quantum Approximate Optimization Algorithm (QAOA)

A variational quantum algorithm for solving combinatorial optimization problems.
Used for problems like Max-Cut, traveling salesman, and scheduling.
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


def create_cost_layer(qc, gamma, edges):
    """
    Apply the cost/problem unitary: e^(-iγH_C)

    For Max-Cut: H_C = Σ_{(i,j)∈E} (1 - Z_i Z_j) / 2

    Args:
        qc: QuantumCircuit
        gamma: Cost layer parameter
        edges: List of edges (i, j) in the graph
    """
    for i, j in edges:
        # e^(-iγ(1-ZZ)/2) = e^(-iγ/2) * e^(iγZZ/2)
        # RZZ(θ)|ψ⟩ = e^(-iθZZ/2)|ψ⟩
        qc.rzz(gamma, i, j)


def create_mixer_layer(qc, beta, n_qubits):
    """
    Apply the mixer unitary: e^(-iβH_B)

    Standard mixer: H_B = Σ_i X_i

    Args:
        qc: QuantumCircuit
        beta: Mixer layer parameter
        n_qubits: Number of qubits
    """
    for i in range(n_qubits):
        qc.rx(2 * beta, i)


def create_qaoa_circuit(n_qubits, edges, gammas, betas):
    """
    Create QAOA circuit for Max-Cut problem.

    Args:
        n_qubits: Number of qubits (nodes in graph)
        edges: List of edges (i, j)
        gammas: Cost layer parameters
        betas: Mixer layer parameters

    Returns:
        QuantumCircuit for QAOA
    """
    p = len(gammas)  # Number of QAOA layers
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial state: uniform superposition
    for i in range(n_qubits):
        qc.h(i)

    qc.barrier()

    # Apply p layers of cost and mixer
    for layer in range(p):
        # Cost layer
        create_cost_layer(qc, gammas[layer], edges)
        qc.barrier()

        # Mixer layer
        create_mixer_layer(qc, betas[layer], n_qubits)

        if layer < p - 1:
            qc.barrier()

    qc.barrier()

    # Measure all qubits
    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def compute_maxcut_value(bitstring, edges):
    """
    Compute the Max-Cut value for a given bitstring.

    Args:
        bitstring: Binary string representing node partition
        edges: List of edges

    Returns:
        Number of edges cut
    """
    cut_value = 0
    for i, j in edges:
        # Edge is cut if nodes are in different partitions
        if bitstring[i] != bitstring[j]:
            cut_value += 1
    return cut_value


def compute_expectation(counts, edges, shots):
    """
    Compute expected Max-Cut value from measurement counts.

    Args:
        counts: Measurement counts
        edges: Graph edges
        shots: Total shots

    Returns:
        Expected cut value
    """
    expectation = 0.0

    for bitstring, count in counts.items():
        bitstring = bitstring.replace(' ', '')
        # Reverse bitstring (Qiskit convention)
        bits = bitstring[::-1]
        cut_value = compute_maxcut_value(bits, edges)
        expectation += cut_value * count / shots

    return expectation


def run_qaoa_iteration(gammas, betas, n_qubits, edges, backend, sampler, shots=1024):
    """
    Run one iteration of QAOA.

    Args:
        gammas: Cost parameters
        betas: Mixer parameters
        n_qubits: Number of qubits
        edges: Graph edges
        backend: IBM Quantum backend
        sampler: Sampler primitive
        shots: Number of shots

    Returns:
        Expected cut value
    """
    # Create QAOA circuit
    qc = create_qaoa_circuit(n_qubits, edges, gammas, betas)

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
    exp_val = compute_expectation(counts, edges, shots)
    return exp_val, counts


def run_qaoa(n_qubits=4, p=2, max_iterations=5, shots=1024):
    """
    Run QAOA for Max-Cut on a simple graph.

    Args:
        n_qubits: Number of nodes in graph
        p: Number of QAOA layers
        max_iterations: Maximum optimization iterations
        shots: Number of shots per measurement

    Returns:
        Dictionary with results
    """
    # Define a simple graph (4-node cycle)
    # 0 -- 1
    # |    |
    # 3 -- 2
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    max_cut = 4  # Optimal cut for this graph

    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
    print(f"Using backend: {backend.name}")

    sampler = Sampler(mode=backend)

    print(f"\nRunning QAOA for Max-Cut")
    print(f"Graph: {n_qubits} nodes, {len(edges)} edges")
    print(f"Edges: {edges}")
    print(f"QAOA layers (p): {p}")
    print(f"Optimal Max-Cut: {max_cut}")

    # Initial parameters
    np.random.seed(42)
    gammas = np.random.uniform(0, np.pi, p)
    betas = np.random.uniform(0, np.pi / 2, p)

    # Simple optimization (for demonstration)
    best_expectation = 0.0
    best_params = (gammas.copy(), betas.copy())
    best_counts = {}
    expectations = []

    for iteration in range(max_iterations):
        print(f"\nIteration {iteration + 1}/{max_iterations}")

        expectation, counts = run_qaoa_iteration(
            gammas, betas, n_qubits, edges, backend, sampler, shots
        )
        expectations.append(expectation)
        print(f"  Expected cut value: {expectation:.3f}")

        if expectation > best_expectation:
            best_expectation = expectation
            best_params = (gammas.copy(), betas.copy())
            best_counts = counts

        # Simple parameter update (random perturbation for demo)
        gammas = best_params[0] + 0.1 * np.random.randn(p)
        betas = best_params[1] + 0.1 * np.random.randn(p)

    # Create final circuit
    final_circuit = create_qaoa_circuit(n_qubits, edges, best_params[0], best_params[1])

    return {
        'best_expectation': best_expectation,
        'best_gammas': best_params[0],
        'best_betas': best_params[1],
        'expectations': expectations,
        'counts': best_counts,
        'edges': edges,
        'max_cut': max_cut,
        'n_qubits': n_qubits,
        'p': p,
        'backend': backend.name,
        'circuit': final_circuit,
        'shots': shots
    }


def analyze_results(results):
    """Analyze QAOA results."""
    print("\n" + "=" * 60)
    print("QAOA RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Nodes: {results['n_qubits']}")
    print(f"Edges: {results['edges']}")
    print(f"QAOA layers: {results['p']}")

    print(f"\nOptimization history:")
    for i, exp in enumerate(results['expectations']):
        print(f"  Iteration {i+1}: {exp:.3f}")

    print(f"\nBest parameters:")
    print(f"  Gammas: {results['best_gammas']}")
    print(f"  Betas: {results['best_betas']}")

    print(f"\nResults:")
    print(f"  Best expected cut: {results['best_expectation']:.3f}")
    print(f"  Optimal cut value: {results['max_cut']}")
    approximation_ratio = results['best_expectation'] / results['max_cut']
    print(f"  Approximation ratio: {approximation_ratio:.3f}")

    # Find best solution
    counts = results['counts']
    if counts:
        print(f"\nTop measurement outcomes:")
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for bitstring, count in sorted_counts[:5]:
            bits = bitstring.replace(' ', '')[::-1]
            cut_val = compute_maxcut_value(bits, results['edges'])
            percentage = count / results['shots'] * 100
            print(f"  {bitstring} -> cut={cut_val}: {count} ({percentage:.1f}%)")

    print(f"\nQAOA explanation:")
    print("  1. Start with uniform superposition |+⟩^⊗n")
    print("  2. Apply p alternating layers of:")
    print("     - Cost unitary e^(-iγH_C) encoding the problem")
    print("     - Mixer unitary e^(-iβH_B) for exploration")
    print("  3. Measure to get candidate solutions")
    print("  4. Classical optimizer updates γ, β to maximize cost")

    print(f"\nApplications:")
    print("  - Combinatorial optimization (Max-Cut, TSP)")
    print("  - Portfolio optimization")
    print("  - Scheduling problems")
    print("  - Graph partitioning")

    print("\nFinal QAOA circuit:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing QAOA on IBM Quantum hardware...")
        print("\nQAOA is a variational algorithm for combinatorial optimization.")
        print("We'll solve the Max-Cut problem on a 4-node graph.\n")

        # Configuration
        n_qubits = 4
        p = 1  # QAOA layers (reduced for hardware)
        max_iterations = 3

        results = run_qaoa(n_qubits, p, max_iterations, shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
