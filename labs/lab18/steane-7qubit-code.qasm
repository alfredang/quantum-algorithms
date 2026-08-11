// Steane's 7-Qubit Error Correcting Code
// [[7,1,3]] CSS code based on Hamming [7,4,3]
// More efficient than Shor code (7 vs 9 qubits)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[7];
creg c[1];

// Input qubit is q[0] (initialized to |0⟩)
// To encode |1⟩, add: x q[0];
// To encode |+⟩, add: h q[0];

// === ENCODING ===
// Initialize check qubits in superposition
h q[4];
h q[5];
h q[6];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6];

// CNOT network based on Hamming code structure
// Creates entanglement pattern for error correction
cx q[4], q[0];
cx q[4], q[2];
cx q[5], q[1];
cx q[5], q[2];
cx q[6], q[3];
cx q[6], q[4];
cx q[6], q[5];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6];

// === ERROR (optional - uncomment one to test) ===
// X error on qubit 2:
// x q[2];
// Z error on qubit 5:
// z q[5];
// Y error:
// y q[3];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6];

// === DECODING ===
// (In full implementation, syndrome measurement goes here)
// Syndrome identifies which qubit has error

// Reverse CNOT network
cx q[6], q[5];
cx q[6], q[4];
cx q[6], q[3];
cx q[5], q[2];
cx q[5], q[1];
cx q[4], q[2];
cx q[4], q[0];

// Reverse Hadamards
h q[4];
h q[5];
h q[6];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6];

// Measure logical qubit
measure q[0] -> c[0];

// Steane code properties:
// - [[7,1,3]] code: 7 physical, 1 logical, distance 3
// - Corrects any single-qubit X, Y, or Z error
// - CSS code structure allows transversal gates
// - Based on classical Hamming [7,4,3] code
//
// Stabilizer generators:
// X-type: X₀X₂X₄X₆, X₁X₂X₅X₆, X₃X₄X₅X₆
// Z-type: Z₀Z₂Z₄Z₆, Z₁Z₂Z₅Z₆, Z₃Z₄Z₅Z₆
