// VQE Ansatz for H₂ molecule (2 qubits)
// Hardware-efficient ansatz with optimized parameters
// Measures in Z basis (for ZZ term of Hamiltonian)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

// Layer 1: Ry rotations (example parameters)
ry(0.5) q[0];
ry(1.2) q[1];

// Entanglement
cx q[0], q[1];

barrier q[0], q[1];

// Layer 2: Ry rotations
ry(-0.8) q[0];
ry(0.3) q[1];

barrier q[0], q[1];

// Measure in Z basis (for ZZ term)
measure q[0] -> c[0];
measure q[1] -> c[1];

// For XX measurement, add H gates before measurement
// For YY measurement, add Sdg then H before measurement
