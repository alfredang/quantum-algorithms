// Superdense Coding
// Send 2 classical bits using 1 qubit + shared entanglement
// Message: "11"
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

// Create entangled Bell pair |Phi+>
h q[0];
cx q[0], q[1];

barrier q[0], q[1];

// Alice encodes message "11" on her qubit (q0)
// 00: I, 01: X, 10: Z, 11: ZX
z q[0];  // For bit 1
x q[0];  // For bit 0

barrier q[0], q[1];

// Bob performs Bell measurement
cx q[0], q[1];
h q[0];

barrier q[0], q[1];

// Measure to decode message
measure q[0] -> c[0];
measure q[1] -> c[1];
