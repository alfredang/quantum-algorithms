// Bernstein-Vazirani Algorithm
// Finds hidden string s in f(x) = s.x (mod 2) with 1 query
// This example: secret string s = "101" (5 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];  // 3 input + 1 ancilla
creg c[3];

// Initialize ancilla to |1>
x q[3];

// Apply Hadamard to all qubits
h q[0];
h q[1];
h q[2];
h q[3];

barrier q[0], q[1], q[2], q[3];

// Oracle for s = "101": CNOT from positions where s[i] = 1
cx q[0], q[3];  // s[0] = 1
// s[1] = 0, no gate
cx q[2], q[3];  // s[2] = 1

barrier q[0], q[1], q[2], q[3];

// Apply Hadamard to input qubits
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Measure to reveal secret string s
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
