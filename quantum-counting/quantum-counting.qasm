// Quantum Counting (simplified version)
// Counts solutions in a 2-qubit search space using 2 counting qubits
// Marked state: |11⟩ (1 solution out of 4)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];  // 2 counting + 2 search
creg c[2];

// Initialize search register in superposition
h q[2];
h q[3];

// Apply Hadamard to counting qubits
h q[0];
h q[1];

barrier q[0], q[1], q[2], q[3];

// Controlled Grover iteration (controlled by q[0])
// Oracle: mark |11⟩
ccz q[0], q[2], q[3];

// Diffusion (controlled)
// Simplified for demonstration
ch q[0], q[2];
ch q[0], q[3];
cx q[0], q[2];
cx q[0], q[3];
ccz q[0], q[2], q[3];
cx q[0], q[2];
cx q[0], q[3];
ch q[0], q[2];
ch q[0], q[3];

barrier q[0], q[1], q[2], q[3];

// Controlled Grover^2 (controlled by q[1])
// Two Grover iterations
ccz q[1], q[2], q[3];
ch q[1], q[2];
ch q[1], q[3];
cx q[1], q[2];
cx q[1], q[3];
ccz q[1], q[2], q[3];
cx q[1], q[2];
cx q[1], q[3];
ch q[1], q[2];
ch q[1], q[3];

// Second iteration
ccz q[1], q[2], q[3];
ch q[1], q[2];
ch q[1], q[3];
cx q[1], q[2];
cx q[1], q[3];
ccz q[1], q[2], q[3];
cx q[1], q[2];
cx q[1], q[3];
ch q[1], q[2];
ch q[1], q[3];

barrier q[0], q[1], q[2], q[3];

// Inverse QFT on counting qubits
swap q[0], q[1];
h q[0];
cp(-pi/2) q[0], q[1];
h q[1];

barrier q[0], q[1], q[2], q[3];

// Measure counting qubits
measure q[0] -> c[0];
measure q[1] -> c[1];

// Result encodes θ where sin²(πθ) = M/N = 1/4
