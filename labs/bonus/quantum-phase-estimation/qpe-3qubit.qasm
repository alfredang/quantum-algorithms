// Quantum Phase Estimation (3 counting qubits)
// Estimates phase φ = 0.25 (binary: 0.01 = 1/4)
// U = P(π/2), eigenstate |1⟩
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];  // 3 counting + 1 target
creg c[3];

// Prepare eigenstate |1⟩ on target qubit
x q[3];

// Apply Hadamard to counting qubits
h q[0];
h q[1];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Controlled-U^(2^j) operations
// U = P(2π * 0.25) = P(π/2)
// U^1 = P(π/2), U^2 = P(π), U^4 = P(2π) = I

// q[0] controls U^1 = P(π/2)
cp(pi/2) q[0], q[3];

// q[1] controls U^2 = P(π)
cp(pi) q[1], q[3];

// q[2] controls U^4 = P(2π) = I (no gate needed)

barrier q[0], q[1], q[2], q[3];

// Inverse QFT
// Swap q[0] and q[2]
swap q[0], q[2];

// Inverse QFT rotations
h q[0];
cp(-pi/2) q[0], q[1];
h q[1];
cp(-pi/4) q[0], q[2];
cp(-pi/2) q[1], q[2];
h q[2];

barrier q[0], q[1], q[2], q[3];

// Measure counting qubits
// Expected result: |010⟩ = 2 -> phase = 2/8 = 0.25
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
