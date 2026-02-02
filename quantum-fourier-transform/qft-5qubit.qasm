// Quantum Fourier Transform (5 qubits)
// Transforms computational basis to Fourier basis
// Input: |10101> (21 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[5];

// Prepare input state |10101>
x q[0];
x q[2];
x q[4];

barrier q[0], q[1], q[2], q[3], q[4];

// === QFT ===

// Qubit 4 (MSB)
h q[4];
cp(pi/2) q[3], q[4];
cp(pi/4) q[2], q[4];
cp(pi/8) q[1], q[4];
cp(pi/16) q[0], q[4];

// Qubit 3
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

barrier q[0], q[1], q[2], q[3], q[4];

// Swap for bit reversal
swap q[0], q[4];
swap q[1], q[3];

barrier q[0], q[1], q[2], q[3], q[4];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
