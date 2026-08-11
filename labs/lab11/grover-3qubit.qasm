// Grover's Algorithm (3 qubits, searching for |101>)
// Target state: |101> (5 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[3];

// Initialize superposition
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2];

// === Grover iteration 1 ===

// Oracle: mark |101> (flip phase when q0=1, q1=0, q2=1)
x q[1];  // Flip q1 to convert |101> check to all-ones check
ccx q[0], q[1], q[2];  // Toffoli as part of phase oracle
// Apply Z to q2 controlled by q0,q1 (using decomposition)
h q[2];
ccx q[0], q[1], q[2];
h q[2];
x q[1];  // Restore q1

barrier q[0], q[1], q[2];

// Diffusion operator
h q[0];
h q[1];
h q[2];
x q[0];
x q[1];
x q[2];
// Multi-controlled Z (CCZ)
h q[2];
ccx q[0], q[1], q[2];
h q[2];
x q[0];
x q[1];
x q[2];
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2];

// === Grover iteration 2 ===

// Oracle
x q[1];
h q[2];
ccx q[0], q[1], q[2];
h q[2];
x q[1];

barrier q[0], q[1], q[2];

// Diffusion
h q[0];
h q[1];
h q[2];
x q[0];
x q[1];
x q[2];
h q[2];
ccx q[0], q[1], q[2];
h q[2];
x q[0];
x q[1];
x q[2];
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
