"""
Activity 2 — Visualising a Qubit on the Bloch Sphere
Topic 2: Introduction to Quantum Computing Systems  ·  LO2

Builds single-qubit states in Qiskit and plots them on the Bloch sphere so you can
SEE what a gate does: which gates move the vector between the poles, and which
rotate it around the equator without changing the Z-basis probabilities.

Runs on the local statevector simulator — no IBM Quantum account required.

Run:  python labs/lab02/main.py
      (figures are written to labs/lab02/out/)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")            # write files instead of opening windows
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def show(qc, name, description):
    """Print the state vector and save the Bloch-sphere plot."""
    sv = Statevector(qc)
    amps = np.asarray(sv)
    # Bloch vector components: <X>, <Y>, <Z>
    a, b = amps[0], amps[1]
    bx = 2 * (a.conj() * b).real
    by = 2 * (a.conj() * b).imag
    bz = abs(a) ** 2 - abs(b) ** 2
    p0, p1 = abs(a) ** 2, abs(b) ** 2

    print(f"\n{name}: {description}")
    print(f"   statevector : [{a:.4f}, {b:.4f}]")
    print(f"   Bloch vector: x={bx:+.3f}  y={by:+.3f}  z={bz:+.3f}")
    print(f"   P(0)={p0:.3f}   P(1)={p1:.3f}")

    fig = plot_bloch_multivector(sv)
    path = os.path.join(OUT, f"{name}.png")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"   saved -> {os.path.relpath(path)}")
    return bx, by, bz, p0


print("=" * 68)
print("Activity 2 — the Bloch sphere")
print("=" * 68)

# STEP 3 — |0>, the north pole
qc = QuantumCircuit(1)
_, _, bz, _ = show(qc, "01-ket0", "|0> — vector at the NORTH pole")
assert np.isclose(bz, 1.0)

# STEP 4 — X flips to |1>, the south pole
qc = QuantumCircuit(1); qc.x(0)
_, _, bz, _ = show(qc, "02-ket1", "X|0> = |1> — vector at the SOUTH pole")
assert np.isclose(bz, -1.0)

# STEP 5 — H creates |+>, on the equator at +x
qc = QuantumCircuit(1); qc.h(0)
bx, _, bz, p0 = show(qc, "03-plus", "H|0> = |+> — on the EQUATOR at +x")
assert np.isclose(bx, 1.0) and np.isclose(bz, 0.0) and np.isclose(p0, 0.5)

# STEP 6 — H then Z gives |->, equator at -x
qc = QuantumCircuit(1); qc.h(0); qc.z(0)
bx, _, _, _ = show(qc, "04-minus", "Z H|0> = |-> — on the EQUATOR at -x")
assert np.isclose(bx, -1.0)

# STEP 7 — an arbitrary Ry rotation
qc = QuantumCircuit(1); qc.ry(np.pi / 4, 0)
_, _, bz, p0 = show(qc, "05-ry-pi-4", "Ry(pi/4)|0> — an arbitrary superposition")
print(f"   cos^2(theta/2) with theta=pi/4 -> P(0) = {np.cos(np.pi/8)**2:.3f}")
assert np.isclose(p0, np.cos(np.pi / 8) ** 2)

# STEP 8 — S after H rotates around the equator; Z-basis probabilities unchanged
qc = QuantumCircuit(1); qc.h(0); qc.s(0)
bx, by, bz, p0 = show(qc, "06-h-then-s", "S H|0> — phase gate rotates AROUND the equator")
assert np.isclose(by, 1.0) and np.isclose(bz, 0.0) and np.isclose(p0, 0.5)

print("\n" + "=" * 68)
print("TEST IT")
print("=" * 68)
print("|0> at the north pole (z=+1)                       : PASS")
print("X moves it to the south pole (z=-1)                : PASS")
print("H places it on the equator at +x, P(0)=P(1)=0.5    : PASS")
print("S rotates around the equator (x -> y), P unchanged : PASS")
print("\nKey insight: the S gate changed the PHASE (x -> y) but NOT the")
print("Z-basis measurement probabilities. Phase is invisible to a Z")
print("measurement — yet it is exactly what quantum interference uses.")
print(f"\nAll figures saved in {os.path.relpath(OUT)}/")
