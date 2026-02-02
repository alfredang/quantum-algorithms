// E91 Protocol - Quantum Key Distribution
// Based on entanglement and Bell inequality
// Security guaranteed by violation of CHSH inequality
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];  // q[0]: Alice's qubit, q[1]: Bob's qubit
creg c[2];

// === Create entangled Bell pair ===
// |Φ⁺⟩ = (|00⟩ + |11⟩) / √2
h q[0];
cx q[0], q[1];

barrier q[0], q[1];

// === Measurement bases ===
// Alice's bases: A1(0°), A2(22.5°), A3(45°)
// Bob's bases:   B1(22.5°), B2(45°), B3(67.5°)
//
// For key generation: use A2=B1 or A3=B2 (matching bases)
// For Bell test: use other combinations

// Example: Both measure in 22.5° basis (A2 and B1)
// Ry(-2θ) before Z-measurement = measurement in θ direction

// Alice measures in A2 basis (π/8 = 22.5°)
ry(-pi/4) q[0];

// Bob measures in B1 basis (π/8 = 22.5°)
ry(-pi/4) q[1];

barrier q[0], q[1];

// Measure both qubits
measure q[0] -> c[0];
measure q[1] -> c[1];

// === CHSH Bell Test ===
// For Bell test, use these basis combinations:
// S = E(A1,B1) - E(A1,B3) + E(A3,B1) + E(A3,B3)
//
// Alternative measurement configurations:
//
// A1 (0°) with B1 (22.5°): Remove both Ry gates, add ry(-pi/4) q[1]
// A1 (0°) with B3 (67.5°): Remove both Ry gates, add ry(-3*pi/4) q[1]
// A3 (45°) with B1 (22.5°): Use ry(-pi/2) q[0]; ry(-pi/4) q[1]
// A3 (45°) with B3 (67.5°): Use ry(-pi/2) q[0]; ry(-3*pi/4) q[1]
//
// Classical bound: |S| ≤ 2
// Quantum bound: |S| ≤ 2√2 ≈ 2.83
// Quantum mechanics predicts S = 2√2 for ideal Bell pairs
//
// If |S| > 2, Bell inequality is violated
// → Confirms quantum entanglement
// → Guarantees secure key distribution (no eavesdropper)
