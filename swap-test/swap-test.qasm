// SWAP Test Circuit
// Compares two quantum states |ψ⟩ and |φ⟩
// P(ancilla=0) = (1 + |⟨ψ|φ⟩|²) / 2
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];  // q[0]: ancilla, q[1]: |ψ⟩, q[2]: |φ⟩
creg c[1];

// Prepare state |ψ⟩ on q[1]
// Example: |+⟩ = H|0⟩
h q[1];

// Prepare state |φ⟩ on q[2]
// Example: |+⟩ = H|0⟩ (same state for overlap = 1)
h q[2];

barrier q[0], q[1], q[2];

// SWAP Test
// Step 1: Hadamard on ancilla
h q[0];

// Step 2: Controlled-SWAP (Fredkin gate)
// CSWAP = controlled swap of q[1] and q[2] based on q[0]
// Decomposition using Toffoli and CNOT
cx q[2], q[1];
ccx q[0], q[1], q[2];
cx q[2], q[1];

// Step 3: Hadamard on ancilla
h q[0];

barrier q[0], q[1], q[2];

// Step 4: Measure ancilla
measure q[0] -> c[0];

// Results:
// If |ψ⟩ = |φ⟩ (identical): P(0) = 1.0, overlap = 1.0
// If |ψ⟩ ⊥ |φ⟩ (orthogonal): P(0) = 0.5, overlap = 0.0
// General: P(0) = (1 + |⟨ψ|φ⟩|²) / 2
//
// To test orthogonal states:
// Change q[2] preparation to: x q[2]; (makes |φ⟩ = |1⟩)
// Or use: h q[2]; z q[2]; (makes |φ⟩ = |-⟩)
