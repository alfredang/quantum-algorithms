// 3-Qubit Phase-Flip Error Correction Code
// Protects against single Z (phase-flip) errors
// Encoding: |0> -> |+++>, |1> -> |--->
OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];  // 3 data + 2 ancilla
creg c[5];

// Prepare logical |1>
x q[0];

// Encode for phase-flip code (in X basis)
h q[0];
cx q[0], q[1];
cx q[0], q[2];

barrier q[0], q[1], q[2], q[3], q[4];

// Simulate phase-flip error on qubit 1
z q[1];

barrier q[0], q[1], q[2], q[3], q[4];

// Syndrome measurement in X basis
// Transform to computational basis
h q[0];
h q[1];
h q[2];

// Measure parities into ancilla
cx q[0], q[3];
cx q[1], q[3];
cx q[1], q[4];
cx q[2], q[4];

// Transform back to X basis
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2], q[3], q[4];

// Measure all
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];

// Syndrome interpretation (same as bit-flip):
// 00: no error
// 01: error on q[2]
// 10: error on q[0]
// 11: error on q[1] (our case)
