// Quantum Teleportation
// Teleports |1> state from q0 to q2 using entanglement
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[2];

// Prepare state to teleport: |1>
x q[0];

barrier q[0], q[1], q[2];

// Create Bell pair between q1 and q2
h q[1];
cx q[1], q[2];

barrier q[0], q[1], q[2];

// Bell measurement on q0, q1
cx q[0], q[1];
h q[0];

barrier q[0], q[1], q[2];

// Measure q0 and q1
measure q[0] -> c[0];
measure q[1] -> c[1];

barrier q[0], q[1], q[2];

// Corrections (classically controlled)
// In hardware: use if statements or post-selection
cx q[1], q[2];
cz q[0], q[2];

barrier q[0], q[1], q[2];
