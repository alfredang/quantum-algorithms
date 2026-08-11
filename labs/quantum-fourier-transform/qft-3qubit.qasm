// Quantum Fourier Transform (3 qubits)
// Transforms computational basis to Fourier basis
// Input: |101> (5 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[3];

// Prepare input state |101>
x q[0];
x q[2];

barrier q[0], q[1], q[2];

// === QFT ===

// Qubit 2 (MSB)
h q[2];
// Controlled rotations
cp(pi/2) q[1], q[2];
cp(pi/4) q[0], q[2];

// Qubit 1
h q[1];
cp(pi/2) q[0], q[1];

// Qubit 0 (LSB)
h q[0];

barrier q[0], q[1], q[2];

// Swap for bit reversal
swap q[0], q[2];

barrier q[0], q[1], q[2];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
