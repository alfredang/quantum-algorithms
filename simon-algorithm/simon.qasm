// Simon's Algorithm
// Finds hidden period s where f(x) = f(y) iff x XOR y in {0, s}
// This example: secret string s = "11" (3 in decimal)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];  // 2 input + 2 output
creg c[2];

// Apply Hadamard to input register
h q[0];
h q[1];

barrier q[0], q[1], q[2], q[3];

// Oracle: copy input to output, then XOR with s if control bit is 1
// Copy x to output: |x>|0> -> |x>|x>
cx q[0], q[2];
cx q[1], q[3];

// XOR output with s="11" controlled by q[0]
cx q[0], q[2];
cx q[0], q[3];

barrier q[0], q[1], q[2], q[3];

// Apply Hadamard to input register
h q[0];
h q[1];

barrier q[0], q[1], q[2], q[3];

// Measure input register (output y where y.s = 0 mod 2)
measure q[0] -> c[0];
measure q[1] -> c[1];
