// Quantum Fourier Transform (4 qubits)
// Transforms computational basis to Fourier basis
// Input: |1010> (10 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];

// Prepare input state |1010>
x q[1];
x q[3];

barrier q[0], q[1], q[2], q[3];

// === QFT ===

// Qubit 3 (MSB)
h q[3];
cp(pi/2) q[2], q[3];
cp(pi/4) q[1], q[3];
cp(pi/8) q[0], q[3];

// Qubit 2
h q[2];
cp(pi/2) q[1], q[2];
cp(pi/4) q[0], q[2];

// Qubit 1
h q[1];
cp(pi/2) q[0], q[1];

// Qubit 0 (LSB)
h q[0];

barrier q[0], q[1], q[2], q[3];

// Swap for bit reversal
swap q[0], q[3];
swap q[1], q[2];

barrier q[0], q[1], q[2], q[3];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
