// Shor's 9-Qubit Error Correcting Code
// First quantum error correcting code
// Protects against arbitrary single-qubit errors
OPENQASM 2.0;
include "qelib1.inc";

qreg q[9];
creg c[1];

// Initialize: prepare |+⟩ for demonstration
h q[0];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8];

// === ENCODING ===
// Step 1: Phase-flip encoding (outer code)
// Copy q[0] to create 3 logical blocks
cx q[0], q[3];
cx q[0], q[6];

// Step 2: Create superposition in each block
h q[0];
h q[3];
h q[6];

// Step 3: Bit-flip encoding within each block (inner code)
// Block 1: q[0,1,2]
cx q[0], q[1];
cx q[0], q[2];

// Block 2: q[3,4,5]
cx q[3], q[4];
cx q[3], q[5];

// Block 3: q[6,7,8]
cx q[6], q[7];
cx q[6], q[8];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8];

// === ERROR (optional - uncomment one to test) ===
// X error on qubit 1:
// x q[1];
// Z error on qubit 4:
// z q[4];
// Y error on qubit 7:
// y q[7];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8];

// === DECODING ===
// (In full implementation, syndrome measurement and correction would go here)

// Reverse bit-flip encoding
cx q[0], q[2];
cx q[0], q[1];
cx q[3], q[5];
cx q[3], q[4];
cx q[6], q[8];
cx q[6], q[7];

// Reverse Hadamards
h q[0];
h q[3];
h q[6];

// Reverse phase-flip encoding
cx q[0], q[6];
cx q[0], q[3];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8];

// Measure recovered qubit
measure q[0] -> c[0];

// Logical states:
// |0⟩_L = (|000⟩+|111⟩)(|000⟩+|111⟩)(|000⟩+|111⟩)/2√2
// |1⟩_L = (|000⟩-|111⟩)(|000⟩-|111⟩)(|000⟩-|111⟩)/2√2
//
// Code can correct:
// - Any single-qubit X error (bit flip)
// - Any single-qubit Z error (phase flip)
// - Any single-qubit Y error (both)
