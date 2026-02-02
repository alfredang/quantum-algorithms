// Quantum Amplitude Estimation (3 counting qubits)
// Estimates amplitude a = 0.25 (sin²(π/6) ≈ 0.25)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];  // 3 counting + 1 state
creg c[3];

// Prepare initial state with amplitude √0.25 = 0.5
// Ry(2*arcsin(0.5)) = Ry(π/3) gives sin²(π/6) = 0.25
ry(pi/3) q[3];

// Apply Hadamard to counting qubits
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Controlled-Q operations
// Q = A S₀ A† Sf is the Grover-like operator

// q[0] controls Q^1
// Sf: phase flip |1⟩
cz q[0], q[3];
// A† = Ry(-π/3)
cry(-pi/3) q[0], q[3];
// S₀: phase flip |0⟩
cx q[0], q[3];
cz q[0], q[3];
cx q[0], q[3];
// A = Ry(π/3)
cry(pi/3) q[0], q[3];

barrier q[0], q[1], q[2], q[3];

// q[1] controls Q^2 (apply twice)
cz q[1], q[3];
cry(-pi/3) q[1], q[3];
cx q[1], q[3];
cz q[1], q[3];
cx q[1], q[3];
cry(pi/3) q[1], q[3];

cz q[1], q[3];
cry(-pi/3) q[1], q[3];
cx q[1], q[3];
cz q[1], q[3];
cx q[1], q[3];
cry(pi/3) q[1], q[3];

barrier q[0], q[1], q[2], q[3];

// q[2] controls Q^4 (apply 4 times)
cz q[2], q[3];
cry(-pi/3) q[2], q[3];
cx q[2], q[3];
cz q[2], q[3];
cx q[2], q[3];
cry(pi/3) q[2], q[3];

cz q[2], q[3];
cry(-pi/3) q[2], q[3];
cx q[2], q[3];
cz q[2], q[3];
cx q[2], q[3];
cry(pi/3) q[2], q[3];

cz q[2], q[3];
cry(-pi/3) q[2], q[3];
cx q[2], q[3];
cz q[2], q[3];
cx q[2], q[3];
cry(pi/3) q[2], q[3];

cz q[2], q[3];
cry(-pi/3) q[2], q[3];
cx q[2], q[3];
cz q[2], q[3];
cx q[2], q[3];
cry(pi/3) q[2], q[3];

barrier q[0], q[1], q[2], q[3];

// Inverse QFT
swap q[0], q[2];
h q[0];
cp(-pi/2) q[0], q[1];
h q[1];
cp(-pi/4) q[0], q[2];
cp(-pi/2) q[1], q[2];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Measure counting qubits
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
