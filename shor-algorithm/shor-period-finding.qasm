// Shor's Algorithm - Period Finding Component
// Simplified for factoring N=15 with a=7
// Finding period r where 7^r mod 15 = 1 (r=4)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[8];  // 4 counting + 4 work qubits
creg c[4];

// Initialize work register to |1>
x q[4];

// Apply Hadamard to counting register
h q[0];
h q[1];
h q[2];
h q[3];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7];

// Controlled modular exponentiation: |j>|1> -> |j>|7^j mod 15>
// This is simplified - full implementation requires controlled multipliers

// For j=1: 7^1 mod 15 = 7
// Controlled-U on q[0]: multiply by 7 mod 15
// (simplified representation)
cx q[0], q[5];
cx q[0], q[6];

// For j=2: 7^2 mod 15 = 4
cx q[1], q[6];

// For j=4: 7^4 mod 15 = 1 (identity)
// For j=8: 7^8 mod 15 = 1 (identity)

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7];

// Inverse QFT on counting register
// Swap
swap q[0], q[3];
swap q[1], q[2];

// QFT inverse rotations
h q[0];
cp(-pi/2) q[0], q[1];
h q[1];
cp(-pi/4) q[0], q[2];
cp(-pi/2) q[1], q[2];
h q[2];
cp(-pi/8) q[0], q[3];
cp(-pi/4) q[1], q[3];
cp(-pi/2) q[2], q[3];
h q[3];

barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7];

// Measure counting register to get period information
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];

// Result reveals period r=4
// gcd(7^(4/2) + 1, 15) = gcd(50, 15) = 5
// gcd(7^(4/2) - 1, 15) = gcd(48, 15) = 3
// Factors: 3 and 5
