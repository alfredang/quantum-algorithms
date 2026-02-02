// BB84 Quantum Key Distribution (4 qubits)
// Alice prepares qubits in random bases, Bob measures in random bases
// Example: Alice bits=[1,0,1,0], Alice bases=[Z,X,Z,X], Bob bases=[Z,Z,X,X]
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];

// Alice prepares her qubits
// Qubit 0: bit=1, Z-basis -> |1>
x q[0];

// Qubit 1: bit=0, X-basis -> |+>
h q[1];

// Qubit 2: bit=1, Z-basis -> |1>
x q[2];

// Qubit 3: bit=0, X-basis -> |+>
h q[3];

barrier q[0], q[1], q[2], q[3];

// Bob measures in his bases
// Qubit 0: Z-basis (no H needed)
// Qubit 1: Z-basis (no H needed) - basis mismatch!
// Qubit 2: X-basis
h q[2];
// Qubit 3: X-basis
h q[3];

barrier q[0], q[1], q[2], q[3];

// Measure all qubits
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];

// Sifted key from positions 0,3 where bases match
// Expected: c[0]=1, c[3]=0
