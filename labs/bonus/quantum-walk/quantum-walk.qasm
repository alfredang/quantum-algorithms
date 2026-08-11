// Discrete-Time Quantum Walk (4 positions, 3 steps)
// q[0]: coin qubit (direction)
// q[1-2]: position qubits (4 positions on cycle)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[2];

// Initial state: coin=|0⟩, position=|00⟩ (origin)

// Step 1
// Coin flip (Hadamard)
h q[0];

// Shift operator
// Right shift when coin=|1⟩ (increment position mod 4)
cx q[0], q[1];
ccx q[0], q[1], q[2];

// Left shift when coin=|0⟩ (decrement position mod 4)
x q[0];
ccx q[0], q[1], q[2];
cx q[0], q[1];
x q[0];

barrier q[0], q[1], q[2];

// Step 2
h q[0];

cx q[0], q[1];
ccx q[0], q[1], q[2];
x q[0];
ccx q[0], q[1], q[2];
cx q[0], q[1];
x q[0];

barrier q[0], q[1], q[2];

// Step 3
h q[0];

cx q[0], q[1];
ccx q[0], q[1], q[2];
x q[0];
ccx q[0], q[1], q[2];
cx q[0], q[1];
x q[0];

barrier q[0], q[1], q[2];

// Measure position
measure q[1] -> c[0];
measure q[2] -> c[1];

// Expected: non-uniform distribution over positions
// Quantum walk spreads faster than classical random walk
// Position spread ~ O(n) vs classical O(√n)
