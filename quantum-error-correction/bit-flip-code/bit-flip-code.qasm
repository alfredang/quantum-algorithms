// 3-Qubit Bit-Flip Error Correction Code
// Protects against single X (bit-flip) errors
// Encoding: |0> -> |000>, |1> -> |111>
OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];  // 3 data + 2 ancilla
creg c[5];

// Prepare logical |1>
x q[0];

// Encode: |psi> -> |psi psi psi>
cx q[0], q[1];
cx q[0], q[2];

barrier q[0], q[1], q[2], q[3], q[4];

// Simulate bit-flip error on qubit 1
x q[1];

barrier q[0], q[1], q[2], q[3], q[4];

// Syndrome measurement
// Ancilla q[3]: parity of q[0] and q[1]
cx q[0], q[3];
cx q[1], q[3];

// Ancilla q[4]: parity of q[1] and q[2]
cx q[1], q[4];
cx q[2], q[4];

barrier q[0], q[1], q[2], q[3], q[4];

// Measure all (correction done in post-processing)
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];

// Syndrome interpretation:
// 00: no error
// 01: error on q[2]
// 10: error on q[0]
// 11: error on q[1] (our case)
