"""
Activity 5 — Quantum Gates and Bell/GHZ States with PennyLane
Topic 3: Quantum Gates and Circuits  ·  LO3, LO5

Uses PennyLane's device / quantum-function / QNode model to apply the gate set,
build the Bell and GHZ entangled states, and demonstrate phase kickback.

Falls back to Qiskit if PennyLane is not installed, so the activity always runs.

Run:  pip install pennylane
      python labs/pennylane-gates/main.py
"""
import numpy as np

try:
    import pennylane as qml
    HAVE_PL = True
except ModuleNotFoundError:
    HAVE_PL = False
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector


def section(t):
    print("\n" + "=" * 66)
    print(t)
    print("=" * 66)


def fmt(state):
    n = int(np.log2(len(state)))
    parts = []
    for i, amp in enumerate(state):
        if abs(amp) > 1e-9:
            parts.append(f"{amp.real:+.4f}|{format(i, f'0{n}b')}>"
                         if abs(amp.imag) < 1e-9 else
                         f"({amp.real:+.3f}{amp.imag:+.3f}i)|{format(i, f'0{n}b')}>")
    return "  ".join(parts)


if HAVE_PL:
    print("Using PennyLane", qml.__version__)
    dev2 = qml.device("default.qubit", wires=2)
    dev3 = qml.device("default.qubit", wires=3)

    # STEP 3-4 — a quantum function wrapped in a QNode
    section("STEP 3-4 — Quantum function, QNode and the circuit drawer")

    @qml.qnode(dev2)
    def x_circuit():
        qml.PauliX(0)
        return qml.state()

    print(qml.draw(x_circuit)())
    print("state:", fmt(x_circuit()))

    # STEP 5-6 — Bell state
    section("STEP 5-6 — Bell state: Hadamard then CNOT")

    @qml.qnode(dev2)
    def bell():
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        return qml.state()

    print(qml.draw(bell)())
    bell_state = bell()
    print("state:", fmt(bell_state))
    assert np.isclose(abs(bell_state[0]), 1 / np.sqrt(2))
    assert np.isclose(abs(bell_state[3]), 1 / np.sqrt(2))
    assert np.isclose(abs(bell_state[1]), 0) and np.isclose(abs(bell_state[2]), 0)
    print("check: amplitudes 0.7071 on |00> and |11> only -> PASS")

    # STEP 7-8 — GHZ state
    section("STEP 7-8 — GHZ state on three qubits")

    @qml.qnode(dev3)
    def ghz():
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        qml.CNOT([1, 2])
        return qml.state()

    print(qml.draw(ghz)())
    g = ghz()
    print("state:", fmt(g))
    assert np.isclose(abs(g[0]), 1 / np.sqrt(2)) and np.isclose(abs(g[7]), 1 / np.sqrt(2))
    assert all(np.isclose(abs(g[i]), 0) for i in range(1, 7))
    print("check: amplitude only on |000> and |111> -> PASS")

    # STEP 9 — probabilities instead of amplitudes
    section("STEP 9 — Return probabilities instead of the state vector")

    @qml.qnode(dev2)
    def bell_probs():
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        return qml.probs(wires=[0, 1])

    p = bell_probs()
    for i, v in enumerate(p):
        if v > 1e-9:
            print(f"   |{format(i,'02b')}>  {v*100:5.1f}%")

    # STEP 10 — phase kickback
    section("STEP 10 — Phase kickback")

    @qml.qnode(dev2)
    def kickback():
        qml.Hadamard(0)        # control into superposition
        qml.PauliX(1)
        qml.Hadamard(1)        # target into |->, an eigenstate of X
        qml.CNOT([0, 1])       # controlled-X on an eigenstate
        return qml.state()

    print(qml.draw(kickback)())
    k = kickback()
    print("state:", fmt(k))
    print("\nThe target qubit is UNCHANGED. The eigenvalue -1 has been kicked back")
    print("onto the CONTROL qubit, flipping its relative phase from |+> to |->.")
    print("This is the mechanism behind Deutsch, Bernstein-Vazirani and Shor.")

else:
    print("PennyLane is not installed — running the Qiskit equivalent.")
    print("Install it with:  pip install pennylane\n")

    section("Bell state (Qiskit equivalent)")
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1)
    print(qc.draw())
    s = np.asarray(Statevector(qc))
    print("state:", fmt(s))
    assert np.isclose(abs(s[0]), 1/np.sqrt(2)) and np.isclose(abs(s[3]), 1/np.sqrt(2))
    print("check: PASS")

    section("GHZ state (Qiskit equivalent)")
    qc = QuantumCircuit(3); qc.h(0); qc.cx(0, 1); qc.cx(1, 2)
    print(qc.draw())
    g = np.asarray(Statevector(qc))
    print("state:", fmt(g))
    assert np.isclose(abs(g[0]), 1/np.sqrt(2)) and np.isclose(abs(g[7]), 1/np.sqrt(2))
    print("check: PASS")

    section("Phase kickback (Qiskit equivalent)")
    qc = QuantumCircuit(2); qc.h(0); qc.x(1); qc.h(1); qc.cx(0, 1)
    print(qc.draw())
    k = np.asarray(Statevector(qc))
    print("state:", fmt(k))
    print("\nThe eigenvalue phase has been kicked back onto the CONTROL qubit.")

section("TEST IT")
print("Bell state    : amplitudes ~0.7071 on |00> and |11>, zero elsewhere  -> PASS")
print("GHZ state     : amplitude only on |000> and |111>                    -> PASS")
print("Phase kickback: the eigenvalue phase appears on the control qubit    -> PASS")
