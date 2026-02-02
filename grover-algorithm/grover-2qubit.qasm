// Grover's Algorithm (2 qubits, searching for |11>)
// Quadratic speedup for unstructured search
// Target state: |11> (3 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

// Initialize superposition
h q[0];
h q[1];

barrier q[0], q[1];

// === Grover iteration (1 iteration optimal for 2 qubits) ===

// Oracle: mark |11> with phase flip
// CZ gate flips phase when both qubits are |1>
cz q[0], q[1];

barrier q[0], q[1];

// Diffusion operator (inversion about mean)
h q[0];
h q[1];
x q[0];
x q[1];
cz q[0], q[1];
x q[0];
x q[1];
h q[0];
h q[1];

barrier q[0], q[1];

// Measure
measure q[0] -> c[0];
measure q[1] -> c[1];
