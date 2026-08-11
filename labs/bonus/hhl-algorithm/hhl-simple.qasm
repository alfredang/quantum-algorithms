// Simplified HHL Algorithm (3 qubits)
// Solves Ax = b for simple 2x2 system
// q[0]: ancilla, q[1]: clock, q[2]: state |b⟩
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[1];

// Step 1: |b⟩ already prepared as |0⟩

// Step 2: QPE - Hadamard on clock
h q[1];

barrier q[0], q[1], q[2];

// Controlled-U (simplified e^(iAt))
cp(pi/2) q[1], q[2];

barrier q[0], q[1], q[2];

// Step 3: Inverse QFT on clock (single qubit = just H)
h q[1];

barrier q[0], q[1], q[2];

// Step 4: Eigenvalue inversion
// Controlled rotation on ancilla based on clock state
// When clock=|1⟩ (larger eigenvalue): smaller rotation
cry(pi/3) q[1], q[0];

// When clock=|0⟩ (smaller eigenvalue): larger rotation
x q[1];
cry(pi/2) q[1], q[0];
x q[1];

barrier q[0], q[1], q[2];

// Step 5: Uncompute QPE
h q[1];
cp(-pi/2) q[1], q[2];
h q[1];

barrier q[0], q[1], q[2];

// Step 6: Measure ancilla
// Post-select on ancilla = |1⟩ for valid solution
measure q[0] -> c[0];

// Success: ancilla measured as 1
// The state qubit q[2] then contains |x⟩ = A⁻¹|b⟩
