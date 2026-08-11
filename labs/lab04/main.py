"""
Activity 4 — Building Circuits in IBM Quantum Composer
Topic 3: Quantum Gates and Circuits  ·  LO5

Activity 4 is done in the BROWSER at https://quantum.ibm.com/composer — you drag
gates onto the staves and watch the statevector and probability panels update live.

This script supports that activity from the command line:
  * it prints the OpenQASM 3 you should see in the Composer's code view, and
  * it verifies the state each circuit produces, so you can check your work.

The .qasm files in this folder can be loaded straight into the Composer.

Run:  python labs/quantum-composer/main.py
"""
import os
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))


def probabilities(qc):
    sv = Statevector(qc.remove_final_measurements(inplace=False))
    return {k: round(v, 4) for k, v in sv.probabilities_dict().items() if v > 1e-9}


def show(step, title, qc, expect, explain):
    print("\n" + "=" * 66)
    print(f"{step} — {title}")
    print("=" * 66)
    print(qc.draw())
    probs = probabilities(qc)
    print("Probability panel in the Composer will show:")
    for state in sorted(probs):
        print(f"   |{state}>  {probs[state]*100:5.1f}%")
    print(f"\n{explain}")
    assert set(probs) == set(expect), f"expected {sorted(expect)}, got {sorted(probs)}"
    for k, v in expect.items():
        assert np.isclose(probs[k], v, atol=0.01), f"|{k}> = {probs[k]}, expected {v}"
    print("check: PASS")


print("Activity 4 — IBM Quantum Composer")
print("Open https://quantum.ibm.com/composer and build each circuit below.")
print("Turn on the Statevector and Probabilities panels to watch them change.")

# STEP 3 — X gate on qubit 0
qc = QuantumCircuit(2)
qc.x(0)
show("STEP 3", "Drag an X gate onto qubit 0",
     qc, {"01": 1.0},
     "X flips qubit 0 from |0> to |1>. Qiskit prints the state as |q1 q0>, so the\n"
     "panel reads |01>: qubit 0 is 1, qubit 1 is still 0. The outcome is certain —\n"
     "no superposition yet.")

# STEP 4 — Hadamard instead
qc = QuantumCircuit(2)
qc.h(0)
show("STEP 4", "Replace X with a Hadamard gate",
     qc, {"00": 0.5, "01": 0.5},
     "H puts qubit 0 into an equal superposition, so the probability panel splits\n"
     "50/50. The two qubits are still INDEPENDENT — this is not entanglement.")

# STEP 5-6 — add the CNOT to entangle
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
show("STEP 5-6", "Add a CNOT (control qubit 0, target qubit 1)",
     qc, {"00": 0.5, "11": 0.5},
     "Now only |00> and |11> have probability — |01> and |10> have vanished.\n"
     "That is the signature of ENTANGLEMENT: the qubits can no longer be described\n"
     "independently. This is the Bell state (|00> + |11>)/sqrt(2).")

# STEP 9 — phase gates do not change the Z-basis probabilities
qc = QuantumCircuit(2)
qc.h(0)
qc.s(0)
show("STEP 9", "Add an S gate after the Hadamard",
     qc, {"00": 0.5, "01": 0.5},
     "The probability panel is UNCHANGED at 50/50 — but the STATEVECTOR panel now\n"
     "shows an i on the second amplitude. Phase gates (Z, S, T) alter the phase,\n"
     "which the probability panel cannot show. Phase is what interference uses.")

# ---------------------------------------------------------------- QASM export
print("\n" + "=" * 66)
print("STEP 7-8 — the OpenQASM the Composer generates for the Bell circuit")
print("=" * 66)
qasm = """OPENQASM 3;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];

c = measure q;
"""
print(qasm)
path = os.path.join(HERE, "bell-state.qasm")
with open(path, "w") as f:
    f.write(qasm)
print(f"Written to {os.path.relpath(path)} — load this file in the Composer")
print("to confirm it reproduces the same circuit.")

print("\n" + "=" * 66)
print("TEST IT")
print("=" * 66)
print("The Composer probability panel shows a 50/50 split between |00> and |11>")
print("for the Bell circuit, and the exported OpenQASM contains an 'h'")
print("instruction followed by a 'cx' instruction.")
print("\nAll checks passed.")
