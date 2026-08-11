"""
Quantum Walk

Discrete-time quantum walk on a line/cycle graph.
Provides quadratic speedup for graph search problems.
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


def create_coin_operator(qc, coin_qubit):
    """
    Apply the Hadamard coin operator.

    The coin determines the direction of the walk:
    |0⟩ → walk left
    |1⟩ → walk right

    Args:
        qc: QuantumCircuit
        coin_qubit: Index of coin qubit
    """
    qc.h(coin_qubit)


def create_shift_operator(qc, coin_qubit, position_qubits):
    """
    Apply the conditional shift operator.

    If coin=|0⟩, shift position left (decrement)
    If coin=|1⟩, shift position right (increment)

    For a 2-qubit position register (4 positions: 0,1,2,3 on a cycle):
    - Controlled increment/decrement mod 4

    Args:
        qc: QuantumCircuit
        coin_qubit: Index of coin qubit
        position_qubits: List of position qubit indices
    """
    n_pos = len(position_qubits)

    # Shift right when coin = |1⟩ (increment)
    # Controlled increment on position register
    if n_pos == 2:
        # 2-qubit incrementer controlled by coin
        # |00⟩ → |01⟩ → |10⟩ → |11⟩ → |00⟩
        qc.cx(coin_qubit, position_qubits[0])
        qc.ccx(coin_qubit, position_qubits[0], position_qubits[1])

    # Shift left when coin = |0⟩ (decrement)
    # First flip coin, then controlled decrement, then flip back
    qc.x(coin_qubit)

    if n_pos == 2:
        # 2-qubit decrementer controlled by coin
        # |00⟩ → |11⟩ → |10⟩ → |01⟩ → |00⟩
        qc.ccx(coin_qubit, position_qubits[0], position_qubits[1])
        qc.cx(coin_qubit, position_qubits[0])

    qc.x(coin_qubit)


def create_quantum_walk_circuit(n_steps, n_position_qubits=2):
    """
    Create discrete-time quantum walk circuit on a cycle.

    Args:
        n_steps: Number of walk steps
        n_position_qubits: Number of qubits for position (2^n positions)

    Returns:
        QuantumCircuit for quantum walk
    """
    # Total qubits: 1 coin + n position
    n_qubits = 1 + n_position_qubits
    qc = QuantumCircuit(n_qubits, n_position_qubits)

    coin_qubit = 0
    position_qubits = list(range(1, n_qubits))

    # Initialize: coin in |0⟩, position in |0...0⟩ (origin)
    # Could start in superposition for different behavior

    # Apply n steps of quantum walk
    for step in range(n_steps):
        # 1. Apply coin operator
        create_coin_operator(qc, coin_qubit)

        # 2. Apply shift operator
        create_shift_operator(qc, coin_qubit, position_qubits)

        if step < n_steps - 1:
            qc.barrier()

    qc.barrier()

    # Measure position qubits
    for i, pos_q in enumerate(position_qubits):
        qc.measure(pos_q, i)

    return qc


def create_marked_quantum_walk(n_steps, marked_position=2, n_position_qubits=2):
    """
    Create quantum walk with marked vertex for search.

    Implements a simple quantum walk search by applying
    phase flip at marked position.

    Args:
        n_steps: Number of walk steps
        marked_position: Position to search for (0 to 2^n-1)
        n_position_qubits: Number of position qubits

    Returns:
        QuantumCircuit
    """
    n_qubits = 1 + n_position_qubits
    qc = QuantumCircuit(n_qubits, n_position_qubits)

    coin_qubit = 0
    position_qubits = list(range(1, n_qubits))

    # Start with uniform superposition over positions
    for pq in position_qubits:
        qc.h(pq)

    qc.barrier()

    for step in range(n_steps):
        # Oracle: phase flip at marked position
        # For marked_position = 2 = |10⟩ in 2 qubits
        if marked_position == 0:  # |00⟩
            qc.x(position_qubits[0])
            qc.x(position_qubits[1])
            qc.cz(position_qubits[0], position_qubits[1])
            qc.x(position_qubits[0])
            qc.x(position_qubits[1])
        elif marked_position == 1:  # |01⟩
            qc.x(position_qubits[1])
            qc.cz(position_qubits[0], position_qubits[1])
            qc.x(position_qubits[1])
        elif marked_position == 2:  # |10⟩
            qc.x(position_qubits[0])
            qc.cz(position_qubits[0], position_qubits[1])
            qc.x(position_qubits[0])
        elif marked_position == 3:  # |11⟩
            qc.cz(position_qubits[0], position_qubits[1])

        qc.barrier()

        # Coin flip
        create_coin_operator(qc, coin_qubit)

        # Shift
        create_shift_operator(qc, coin_qubit, position_qubits)

        if step < n_steps - 1:
            qc.barrier()

    qc.barrier()

    # Measure position
    for i, pos_q in enumerate(position_qubits):
        qc.measure(pos_q, i)

    return qc


def run_quantum_walk(n_steps=4, walk_type='simple', shots=1024):
    """
    Run quantum walk on IBM Quantum hardware.

    Args:
        n_steps: Number of walk steps
        walk_type: 'simple' or 'search'
        shots: Number of measurements

    Returns:
        Dictionary with results
    """
    # Connect to IBM Quantum
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_QUANTUM_TOKEN, instance=IBM_QUANTUM_INSTANCE)

    n_qubits = 3  # 1 coin + 2 position
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
    print(f"Using backend: {backend.name}")

    # Create circuit
    if walk_type == 'search':
        marked_position = 2
        qc = create_marked_quantum_walk(n_steps, marked_position)
        print(f"\nQuantum Walk Search")
        print(f"Searching for position: {marked_position}")
    else:
        qc = create_quantum_walk_circuit(n_steps)
        marked_position = None
        print(f"\nSimple Quantum Walk on Cycle")

    print(f"Position qubits: 2 (4 positions: 0,1,2,3)")
    print(f"Walk steps: {n_steps}")
    print("\nCircuit:")
    print(qc.draw())

    # Transpile
    transpiled = transpile(qc, backend, optimization_level=1)
    print(f"\nTranspiled circuit depth: {transpiled.depth()}")

    # Run
    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled], shots=shots)
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
        'counts': counts,
        'n_steps': n_steps,
        'walk_type': walk_type,
        'marked_position': marked_position,
        'job_id': job.job_id(),
        'backend': backend.name,
        'circuit': qc,
        'shots': shots
    }


def analyze_results(results):
    """Analyze quantum walk results."""
    print("\n" + "=" * 60)
    print("QUANTUM WALK RESULTS")
    print("=" * 60)

    print(f"\nBackend: {results['backend']}")
    print(f"Job ID: {results['job_id']}")
    print(f"Walk type: {results['walk_type']}")
    print(f"Steps: {results['n_steps']}")
    if results['marked_position'] is not None:
        print(f"Marked position: {results['marked_position']}")

    counts = results['counts']
    if not counts:
        print("\nNo measurement counts available")
        return

    print(f"\nPosition distribution:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    total = results['shots']

    for bitstring, count in sorted_counts:
        bitstring = bitstring.replace(' ', '')
        position = int(bitstring[::-1], 2)  # Reverse for Qiskit convention
        percentage = count / total * 100
        bar = '█' * int(percentage / 5)
        print(f"  Position {position} ({bitstring}): {count} ({percentage:.1f}%) {bar}")

    # Compute mean position
    mean_pos = 0.0
    for bitstring, count in counts.items():
        bitstring = bitstring.replace(' ', '')
        position = int(bitstring[::-1], 2)
        mean_pos += position * count / total

    print(f"\nMean position: {mean_pos:.2f}")

    # Compare with classical random walk
    print(f"\nComparison with classical random walk:")
    print(f"  Classical: position spread ~ O(√n) after n steps")
    print(f"  Quantum: position spread ~ O(n) after n steps")
    print(f"  Quantum walk spreads quadratically faster!")

    if results['walk_type'] == 'search':
        marked = results['marked_position']
        marked_binary = format(marked, '02b')[::-1]
        marked_count = 0
        for bitstring, count in counts.items():
            bitstring = bitstring.replace(' ', '')[::-1]
            if int(bitstring, 2) == marked:
                marked_count = count
                break
        success_rate = marked_count / total * 100
        print(f"\nSearch success rate for position {marked}: {success_rate:.1f}%")

    print(f"\nQuantum walk explanation:")
    print("  1. Coin qubit determines walk direction")
    print("  2. Hadamard coin creates superposition of directions")
    print("  3. Shift operator moves position based on coin")
    print("  4. Interference creates non-classical distribution")

    print(f"\nApplications:")
    print("  - Graph search algorithms")
    print("  - Element distinctness")
    print("  - Triangle finding")
    print("  - Quantum simulation")

    print("\nCircuit diagram:")
    print(results['circuit'].draw())


if __name__ == "__main__":
    try:
        print("Executing Quantum Walk on IBM Quantum hardware...")
        print("\nQuantum walks provide quadratic speedup for search problems")
        print("and exhibit non-classical spreading behavior.\n")

        # Run simple quantum walk
        results = run_quantum_walk(n_steps=3, walk_type='simple', shots=1024)
        analyze_results(results)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("\nMake sure you have set your IBM Quantum credentials in .env file:")
        print("  IBM_QUANTUM_TOKEN=your_token_here")
        print("  IBM_QUANTUM_INSTANCE=your_instance_here")
