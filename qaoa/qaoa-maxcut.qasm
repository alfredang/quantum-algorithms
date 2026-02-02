// QAOA for Max-Cut (4-node cycle graph, p=1)
// Graph: 0-1-2-3-0 (cycle)
// Optimal cut = 4 (alternating partition)
OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];

// Initial state: uniform superposition
h q[0];
h q[1];
h q[2];
h q[3];

barrier q[0], q[1], q[2], q[3];

// Cost layer: e^(-iγH_C) where H_C = Σ(1-ZZ)/2
// Using γ = π/4 as example parameter
// RZZ(γ) for each edge

// Edge (0,1)
cx q[0], q[1];
rz(pi/4) q[1];
cx q[0], q[1];

// Edge (1,2)
cx q[1], q[2];
rz(pi/4) q[2];
cx q[1], q[2];

// Edge (2,3)
cx q[2], q[3];
rz(pi/4) q[3];
cx q[2], q[3];

// Edge (3,0)
cx q[3], q[0];
rz(pi/4) q[0];
cx q[3], q[0];

barrier q[0], q[1], q[2], q[3];

// Mixer layer: e^(-iβH_B) where H_B = ΣX
// Using β = π/8 as example parameter
// RX(2β) on each qubit

rx(pi/4) q[0];
rx(pi/4) q[1];
rx(pi/4) q[2];
rx(pi/4) q[3];

barrier q[0], q[1], q[2], q[3];

// Measurement
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];

// Expected outcomes for Max-Cut:
// 0101 or 1010 -> cut = 4 (optimal)
// 0011, 1100, 0110, 1001 -> cut = 2
