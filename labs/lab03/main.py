"""
Activity 3 — Superposition and Entanglement on IBM Quantum
Topic 2: Introduction to Quantum Computing Systems  ·  LO2, LO4

Builds a single-qubit superposition circuit and a two-qubit Bell state, then runs
them. By default it runs on the local simulator so the activity always works; pass
--hardware to submit the job to a real IBM Quantum backend.

Run:  python labs/lab03/main.py              # local simulator (noise-free)
      python labs/lab03/main.py --hardware   # real IBM Quantum device
"""
import os
import sys
import argparse

from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile

load_dotenv()
IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE")


def superposition_circuit():
    """One qubit, one Hadamard: a fair quantum coin."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def bell_circuit():
    """H then CNOT — the maximally entangled Bell state (|00> + |11>)/sqrt(2)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)            # superposition on the control qubit
    qc.cx(0, 1)        # CNOT entangles qubit 1 with qubit 0
    qc.measure([0, 1], [0, 1])
    return qc


def run_local(qc, shots=1024):
    """Sample the ideal state vector. Uses qiskit-aer when it is installed, and
    otherwise falls back to Statevector.sample_counts, which ships with Qiskit
    itself — so this activity runs with no extra packages."""
    try:
        from qiskit_aer import AerSimulator
        backend = AerSimulator()
        result = backend.run(transpile(qc, backend), shots=shots).result()
        return result.get_counts(), "AerSimulator (local, noise-free)"
    except ModuleNotFoundError:
        from qiskit.quantum_info import Statevector
        meas = qc.remove_final_measurements(inplace=False)
        counts = Statevector(meas).sample_counts(shots)
        return dict(counts), "Statevector sampler (local, noise-free)"


def run_hardware(qc, shots=1024):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService(channel="ibm_quantum_platform",
                                   token=IBM_QUANTUM_TOKEN,
                                   instance=IBM_QUANTUM_INSTANCE)
    backend = service.least_busy(operational=True, simulator=False,
                                 min_num_qubits=qc.num_qubits)
    print(f"Using backend: {backend.name}")
    tqc = transpile(qc, backend, optimization_level=1)
    print(f"Transpiled depth: {tqc.depth()}")
    job = Sampler(mode=backend).run([tqc], shots=shots)
    print(f"Job submitted: {job.job_id()} — waiting for the result...")
    res = job.result()[0]
    counts = next(getattr(res.data, f).get_counts()
                  for f in dir(res.data)
                  if not f.startswith("_") and hasattr(getattr(res.data, f), "get_counts"))
    return counts, backend.name


def report(name, counts, backend, shots, expected):
    print("\n" + "=" * 62)
    print(f"{name}   (backend: {backend})")
    print("=" * 62)
    for outcome in sorted(counts):
        n = counts[outcome]
        pct = 100 * n / shots
        bar = "#" * int(pct / 2)
        flag = "" if outcome in expected else "   <- noise (ideally impossible)"
        print(f"  |{outcome}>  {n:5d}  {pct:5.1f}%  {bar}{flag}")
    noise = sum(n for o, n in counts.items() if o not in expected)
    print(f"\n  outcomes outside {sorted(expected)}: {noise} shots "
          f"({100*noise/shots:.1f}%)")
    return noise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hardware", action="store_true",
                    help="run on a real IBM Quantum backend instead of the simulator")
    ap.add_argument("--shots", type=int, default=1024)
    args = ap.parse_args()

    runner = run_hardware if args.hardware else run_local
    if args.hardware and not IBM_QUANTUM_TOKEN:
        sys.exit("IBM_QUANTUM_TOKEN is not set. Create labs/.env with:\n"
                 "  IBM_QUANTUM_TOKEN=your_api_token_here\n"
                 "  IBM_QUANTUM_INSTANCE=your_instance_here")

    print("Activity 3 — Superposition and Entanglement")
    print("Step 4: single-qubit superposition")
    qc1 = superposition_circuit()
    print(qc1.draw())
    counts1, backend1 = runner(qc1, args.shots)
    report("SUPERPOSITION — expect ~50/50 over |0> and |1>",
           counts1, backend1, args.shots, {"0", "1"})

    print("\nStep 5: the Bell state")
    qc2 = bell_circuit()
    print(qc2.draw())
    counts2, backend2 = runner(qc2, args.shots)
    noise = report("BELL STATE — expect ~50/50 over |00> and |11> ONLY",
                   counts2, backend2, args.shots, {"00", "11"})

    print("\n" + "=" * 62)
    print("TEST IT")
    print("=" * 62)
    print("The superposition circuit gives roughly 50% |0> and 50% |1>.")
    print("The Bell circuit gives roughly 50% |00> and 50% |11>.")
    if args.hardware:
        print(f"\n|01> and |10> appeared in {100*noise/args.shots:.1f}% of shots.")
        print("These are FORBIDDEN in the ideal state — they are caused by hardware")
        print("noise: gate infidelity, decoherence and readout error.")
    else:
        print("\nOn the noise-free simulator |01> and |10> never appear.")
        print("Re-run with --hardware to see real device noise produce them.")
    print("\nMeasuring one qubit of the Bell pair determines the other with")
    print("certainty — that correlation is entanglement.")


if __name__ == "__main__":
    main()
