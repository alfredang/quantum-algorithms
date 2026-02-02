// Deutsch-Jozsa Algorithm (3 input qubits)
// Determines if f:{0,1}^n -> {0,1} is constant or balanced with 1 query
// This example uses balanced oracle (parity function)
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

// Balanced oracle: f(x) = x0 XOR x1 XOR x2 (parity)
cx q[0], q[3];
cx q[1], q[3];
cx q[2], q[3];

barrier q[0], q[1], q[2], q[3];

// Apply Hadamard to input qubits
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Measure: all 0s = constant, any 1 = balanced
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
