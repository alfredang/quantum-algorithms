"""
Activity 1 — Linear Algebra for Quantum Mechanics in Python
Topic 1: Quantum Physics Fundamentals  ·  LO1

Builds the mathematical objects every quantum algorithm rests on: state vectors,
inner and outer products, unitary and Hermitian operators, eigenvalues, the Born
rule, and tensor products. Pure NumPy — no quantum SDK and no IBM account needed,
so this runs anywhere.

Run:  python labs/linear-algebra/main.py
"""
import numpy as np

np.set_printoptions(precision=4, suppress=True)


def section(title):
    print("\n" + "=" * 66)
    print(title)
    print("=" * 66)


# ---------------------------------------------------------------- basis states
section("STEP 1-3 — Basis states and superposition")

ket0 = np.array([[1], [0]], dtype=complex)   # |0>
ket1 = np.array([[0], [1]], dtype=complex)   # |1>
print("|0> =\n", ket0)
print("|1> =\n", ket1)

# |+> = (|0> + |1>)/sqrt(2)
plus = (ket0 + ket1) / np.sqrt(2)
minus = (ket0 - ket1) / np.sqrt(2)
print("\n|+> =\n", plus)
print("norm of |+> =", np.linalg.norm(plus), " (must be 1.0)")
assert np.isclose(np.linalg.norm(plus), 1.0)


# ---------------------------------------------------------------- operators
section("STEP 4-5 — The Pauli and Hadamard operators, and unitarity")

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)

for name, M in [("X", X), ("Y", Y), ("Z", Z), ("H", H)]:
    unitary = np.allclose(M.conj().T @ M, I)
    print(f"{name}: U-dagger U == I ?  {unitary}")
    assert unitary, f"{name} is not unitary"

print("\nUnitarity is why every quantum gate is reversible and preserves probability.")


# ---------------------------------------------------------------- hermitian
section("STEP 6-7 — Hermitian operators, eigenvalues and eigenvectors")

for name, M in [("X", X), ("Y", Y), ("Z", Z)]:
    herm = np.allclose(M.conj().T, M)
    vals = np.linalg.eigvals(M)
    print(f"{name}: A-dagger == A ? {herm}   eigenvalues = {np.real_if_close(vals)}")
    assert herm, f"{name} is not Hermitian"
    assert np.allclose(vals.imag, 0), f"{name} has complex eigenvalues"

vals, vecs = np.linalg.eig(Z)
print("\nPauli-Z eigen-decomposition:")
for i, v in enumerate(vals):
    print(f"  eigenvalue {np.real_if_close(v):+.0f}  ->  eigenvector {vecs[:, i].real}")
print("These eigenvectors ARE |0> and |1> — the computational basis is the Z basis.")
print("Hermitian => real eigenvalues => a physically measurable observable.")


# ---------------------------------------------------------------- born rule
section("STEP 8 — Inner product and the Born rule")

amp0 = (ket0.conj().T @ plus).item()      # <0|+>
amp1 = (ket1.conj().T @ plus).item()      # <1|+>
p0, p1 = abs(amp0) ** 2, abs(amp1) ** 2
print(f"<0|+> = {amp0:.4f}   ->  P(0) = |<0|+>|^2 = {p0:.4f}")
print(f"<1|+> = {amp1:.4f}   ->  P(1) = |<1|+>|^2 = {p1:.4f}")
print(f"P(0) + P(1) = {p0 + p1:.4f}  (probabilities must sum to 1)")
assert np.isclose(p0, 0.5) and np.isclose(p1, 0.5)
assert np.isclose(p0 + p1, 1.0)

# outer product |0><0| is the projector onto |0>
proj0 = ket0 @ ket0.conj().T
print("\nProjector |0><0| =\n", proj0.real)
print("Born rule via the projector: P(0) = <psi|P0|psi> =",
      float(np.real(plus.conj().T @ proj0 @ plus)))


# ---------------------------------------------------------------- tensor
section("STEP 9-10 — Tensor products build multi-qubit systems")

psi = np.kron(ket0, ket1)                 # |0> tensor |1> = |01>
print("|0> (x) |1> = |01> =", psi.ravel().real, " shape:", psi.shape)
assert psi.shape == (4, 1)

HI = np.kron(H, I)                        # H on qubit 0, identity on qubit 1
print("\nH (x) I is 4x4 and unitary ?",
      HI.shape == (4, 4) and np.allclose(HI.conj().T @ HI, np.eye(4)))
assert np.allclose(HI.conj().T @ HI, np.eye(4))

# a Bell state is NOT a product state — this is entanglement
bell = (np.kron(ket0, ket0) + np.kron(ket1, ket1)) / np.sqrt(2)
print("\nBell state (|00> + |11>)/sqrt(2) =", bell.ravel().real)

# Separability test: reshape to a 2x2 matrix; rank 1 => product state, rank 2 => entangled
def schmidt_rank(two_qubit_state):
    M = two_qubit_state.reshape(2, 2)
    return np.linalg.matrix_rank(M, tol=1e-9)

print("Schmidt rank of |01>       :", schmidt_rank(psi), " -> 1 = separable (product state)")
print("Schmidt rank of Bell state :", schmidt_rank(bell), " -> 2 = ENTANGLED")
assert schmidt_rank(psi) == 1
assert schmidt_rank(bell) == 2

print("\nn qubits span a 2^n dimensional Hilbert space — this exponential growth")
print("is the resource quantum algorithms exploit.")


# ---------------------------------------------------------------- test it
section("TEST IT — all checks")
print("H-dagger H == I                          : PASS")
print("X and Z Hermitian with real eigenvalues  : PASS")
print("Born rule P(0) in |+> == 0.5             : PASS")
print("Tensor product gives a 4-component state : PASS")
print("\nAll assertions passed.")
