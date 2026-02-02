// Deutsch Algorithm
// Determines if f:{0,1}->{0,1} is constant or balanced with 1 query
// This example uses balanced oracle (f(x) = x)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[1];

// Initialize: |0>|1>
x q[1];

// Apply Hadamard to both qubits
h q[0];
h q[1];

barrier q[0], q[1];

// Oracle for balanced function f(x) = x (CNOT)
cx q[0], q[1];

barrier q[0], q[1];

// Apply Hadamard to first qubit
h q[0];

barrier q[0], q[1];

// Measure: 0 = constant, 1 = balanced
measure q[0] -> c[0];
