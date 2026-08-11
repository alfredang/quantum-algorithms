#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the WSQ assessment set for 'Application Integration with Docker and Kubernetes' (TGS-2021010366):
  - Written Assessment (SAQ)  — 5 open-ended KNOWLEDGE questions (K1–K5), aligned to the slides
  - Practical Performance (PP) — 4 PRACTICAL tasks (LO1–LO4), aligned to the in-class activities
Each instrument is produced as a Question Paper and a matching Answer Key (4 DOCX total),
all with the WSQ house cover page (same as the Lesson Plan / Learner Guide). Page 1 is the cover;
page 2 carries Trainee Information + Instructions + Grading; the questions/tasks begin on page 3.
Body: Arial 11.
"""
import os, sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# This script lives in the wsq-assessment skill (.claude/skills/wsq-assessment/) and runs in
# place — it detects the course repo root by walking up to the nearest dir that has a .git
# folder (or both courseware/ and assessment/). Override with env REPO=/path if needed.
def _find_repo():
    env = os.environ.get("REPO")
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")) or \
           (os.path.isdir(os.path.join(d, "courseware")) and os.path.isdir(os.path.join(d, "assessment"))):
            return d
        d = os.path.dirname(d)
    return os.getcwd()

REPO = _find_repo()
# prodoc.py (WSQ cover page + version control + page numbers, same as LP/LG) ships with the
# tertiary-lesson-plan skill. Look for it at the project level first, then the user level.
for _cand in (os.path.join(REPO, ".claude/skills/tertiary-lesson-plan"),
              os.path.expanduser("~/.claude/skills/tertiary-lesson-plan")):
    if os.path.exists(os.path.join(_cand, "prodoc.py")):
        sys.path.insert(0, _cand); break
import prodoc  # cover page + version control + page numbers (same as LP/LG)

# ─── EDIT PER COURSE ────────────────────────────────────────────────────────
TITLE       = "Securing the Future with Quantum Computing and Cryptography"
COURSE_CODE = "TGS-2024043419"
# ────────────────────────────────────────────────────────────────────────────
# The cover page renders prodoc's module-level TGS constant. Override it so the
# assessment cover shows THIS course's ref (works with either prodoc version —
# the older project prodoc has no course_code kwarg).
prodoc.TGS = f"TGS Ref No: {COURSE_CODE}"
OUT   = os.path.join(REPO, "assessment")

# Logos: prefer the course's own courseware/assets, else fall back to the copies bundled
# in this skill (so the assessment builds even outside this project). Replace the course
# logo per course; the Tertiary Infotech logo is the same for every WSQ course.
def _logo(name):
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(REPO, "courseware/assets", name), os.path.join(here, "assets", name)):
        if os.path.exists(p):
            return p
    return None
ORG_LOGO    = _logo("tertiary-infotech-logo.png")
COURSE_LOGO = None   # Tertiary-only cover (as LP/LG)

Q_VER, A_VER = "v11", "v11"   # single standardised version across all four files
BRAND = RGBColor(0x1F, 0x6F, 0xEB); DARK = RGBColor(0x11, 0x18, 0x27); GREY = RGBColor(0x55, 0x5B, 0x66)
# Assessments carry the cover page only — no Document Version Control Record.

# ---------------------------------------------------------------- WRITTEN (KNOWLEDGE)
# (criterion, context, question, [model-answer points]) — each traces to the course slides.
# Mirrors the original TMS paper: 5 open-ended knowledge questions, K1-K5.
WRITTEN = [
 ("K1",
  "A bank needs to exchange encryption keys between two branches over a fibre link and wants the security of the "
  "key exchange to rest on the laws of physics rather than on a mathematical hardness assumption.",
  "Which quantum key distribution protocol should the bank adopt, and explain how it detects the presence of an "
  "eavesdropper on the channel.",
  ["The BB84 protocol, introduced by Bennett and Brassard in 1984 — the first and most widely deployed quantum "
   "key distribution (QKD) protocol.",
   "Alice encodes each random bit in a randomly chosen basis: the rectilinear (Z) basis sends |0> or |1>, and "
   "the diagonal (X) basis sends |+> or |->. Bob measures each arriving qubit in his own randomly chosen basis.",
   "Alice and Bob then publicly compare BASES ONLY (never the bit values) and discard every position where their "
   "bases differed — this step is called sifting and leaves the sifted key.",
   "Eavesdropping is detected because the no-cloning theorem forbids Eve from copying an unknown qubit. To learn "
   "anything she must measure, and measuring in the wrong basis disturbs the state.",
   "An intercept-resend attack introduces roughly a 25% error rate in the sifted key. Alice and Bob sacrifice a "
   "random subset of the key to estimate this error rate; if it exceeds their security threshold they abort and "
   "discard the key. (Slides: Topic 4 — BB84 Quantum Key Distribution; Activity 8.)"]),
 ("K2",
  "A pharmaceutical company is evaluating whether quantum computing can accelerate its drug discovery pipeline, "
  "where the bottleneck is simulating how candidate molecules interact.",
  "What core quantum computing concepts make it possible to model molecular interactions more accurately than "
  "classical computers, and which algorithm is used for this in the near term?",
  ["Superposition — n qubits hold a superposition of all 2^n basis states at once, so the state space available "
   "to the computation grows exponentially with the number of qubits.",
   "Entanglement — correlations between qubits that cannot be factored into independent single-qubit states; "
   "electrons in a molecule are genuinely entangled, so a quantum computer represents them naturally.",
   "Interference — amplitudes can add or cancel, which is what lets a quantum algorithm concentrate probability "
   "on the correct answer rather than searching by brute force.",
   "The near-term algorithm is VQE (the Variational Quantum Eigensolver), a hybrid loop in which a parameterised "
   "quantum circuit prepares a trial state and a classical optimiser tunes the parameters to minimise the energy.",
   "VQE computes the ground-state energy of a molecule — the quantity that drives chemical behaviour. Its shallow "
   "circuits tolerate noise, which is why it is practical on today's NISQ hardware. "
   "(Slides: Topic 7 — Applications and Use Cases; VQE — Simulating Molecules; Activity 15.)"]),
 ("K3",
  "A bank's security team is assessing which of its cryptographic systems are exposed once a large fault-tolerant "
  "quantum computer becomes available.",
  "Which quantum algorithm poses the greatest risk to classical public-key cryptography, how does it work, and "
  "what must the bank do about it?",
  ["Shor's algorithm (Peter Shor, 1994) — it factors large integers and computes discrete logarithms in "
   "polynomial time, breaking RSA, Diffie-Hellman, DSA and elliptic-curve cryptography (ECC/ECDSA).",
   "It works by reducing factoring to PERIOD FINDING: choose a random a coprime to N, then find the period r of "
   "the function a^x mod N. Only the period-finding step is quantum; the rest is classical number theory.",
   "The quantum core puts a counting register into superposition, applies controlled modular exponentiation, then "
   "applies the INVERSE QUANTUM FOURIER TRANSFORM to extract the period from the resulting interference pattern.",
   "The factors are then recovered classically as gcd(a^(r/2) +/- 1, N).",
   "Grover's algorithm is a lesser but real threat to symmetric cryptography: it halves the effective key length, "
   "so AES-128 drops to about 64-bit security while AES-256 remains safe.",
   "The bank must migrate to NIST post-quantum standards — ML-KEM (FIPS 203) for key establishment and ML-DSA "
   "(FIPS 204) or SLH-DSA (FIPS 205) for signatures — and should prioritise long-lived secrets because of the "
   "harvest-now-decrypt-later risk. (Slides: Topic 6 — Shor's Algorithm, The Quantum Threat, PQC; Activities 13-14.)"]),
 ("K4",
  "The Deutsch algorithm is the first algorithm to show a provable quantum advantage: it decides whether a "
  "black-box function f:{0,1} -> {0,1} is constant or balanced using only ONE query, where any classical method "
  "needs two.",
  "Which crucial quantum principle underlies the Deutsch algorithm's ability to solve this problem more "
  "efficiently than classical methods, and how does the algorithm use it?",
  ["The crucial principle is PHASE KICKBACK, combined with quantum interference.",
   "The oracle is implemented reversibly as |x>|y> -> |x>|y XOR f(x)>. The target qubit is prepared in the state "
   "|-> = (|0> - |1>)/sqrt(2), which is an eigenstate of the X operation.",
   "Because |-> is an eigenstate, applying the oracle does not change the target qubit — instead it 'kicks back' "
   "a phase of (-1)^f(x) onto the CONTROL (input) qubit. The information about f moves into the phase.",
   "The input qubit is therefore left in a superposition whose relative phase encodes whether f(0) and f(1) are "
   "equal. A final Hadamard converts that phase difference into a measurable amplitude difference — this is the "
   "interference step.",
   "Measuring the input qubit yields 0 if the function is CONSTANT and 1 if it is BALANCED, after a single oracle "
   "query. The same phase-kickback mechanism drives Deutsch-Jozsa, Bernstein-Vazirani, phase estimation and Shor. "
   "(Slides: Topic 3 — Phase Kickback; Topic 5 — Deutsch Algorithm; Activity 9.)"]),
 ("K5",
  "Every quantum algorithm in this course begins by putting the qubit register into an equal superposition so "
  "that many candidate solutions can be explored in parallel.",
  "Which quantum gate plays this critical role, what does it do to the basis states, and why is it essential to "
  "algorithms such as Grover's search?",
  ["The Hadamard gate (H) — it is the gate that creates superposition.",
   "It maps |0> to |+> = (|0> + |1>)/sqrt(2) and |1> to |-> = (|0> - |1>)/sqrt(2). It is its own inverse "
   "(H·H = I), and it is both unitary and Hermitian.",
   "Applying H to each of n qubits initialised in |0> produces an equal superposition of ALL 2^n basis states, "
   "each with amplitude 1/sqrt(2^n) — this is the parallel exploration step.",
   "On the Bloch sphere H moves the state vector from the pole to the equator, converting a definite Z-basis "
   "value into maximal Z-basis uncertainty.",
   "In Grover's algorithm the Hadamard layer creates the uniform superposition over all N candidates, and "
   "Hadamards also appear inside the diffuser that reflects amplitudes about their mean. Superposition alone is "
   "not enough — interference is what concentrates probability on the marked item. "
   "(Slides: Topic 3 — Hadamard Gate; Topic 5 — Grover's Algorithm; Activities 5 and 11.)"]),
]

# ---------------------------------------------------------------- PRACTICAL (ACTIVITY-BASED)
SCENARIO = (
 "You are part of a consulting team at Qubit Advisors, which specialises in quantum computing solutions for "
 "regulated industries. A large pharmaceutical company has approached your team to explore how quantum computing "
 "can support its research and development pipeline, and how it should prepare its own systems for the arrival of "
 "quantum computers. You will build and explain the quantum circuits that underpin the client's proposed "
 "solution. Complete the seven tasks below; each mirrors a hands-on activity you did in class. For each task, "
 "paste your circuit code (Qiskit or OpenQASM), a screenshot of the circuit diagram or output, and your "
 "explanation as evidence.")

BOX_CAP = "Paste your circuit code and a screenshot of the circuit diagram / output in the box below"
MATH_CAP = "Paste your mathematical working (typed or a clear photograph of your handwriting) in the box below"

PRACTICAL = [
 ("Task 1", "A1",
  "Construct a quantum circuit that ENTANGLES TWO QUBITS starting from the initial state |00>. "
  "Part A — Build the circuit in Qiskit (or IBM Quantum Composer): apply a Hadamard gate to qubit 0, then a CNOT "
  "gate with qubit 0 as control and qubit 1 as target, then measure both qubits. "
  "Part B — Name the resulting state and state the measurement probabilities you expect. "
  "Part C — Run the circuit with at least 1024 shots and paste the resulting histogram. Explain why a small "
  "number of |01> and |10> counts appear when the circuit is run on real hardware. "
  "(Activity 3 — Superposition and Entanglement on IBM Quantum; Activity 4 — IBM Quantum Composer.)",
  BOX_CAP,
  "Part A — Bell state circuit:\n"
  "from qiskit import QuantumCircuit\n"
  "qc = QuantumCircuit(2, 2)\n"
  "qc.h(0)            # superposition on the control qubit\n"
  "qc.cx(0, 1)        # CNOT entangles qubit 1 with qubit 0\n"
  "qc.measure([0, 1], [0, 1])\n\n"
  "OpenQASM equivalent:\n"
  "OPENQASM 3; include \"stdgates.inc\";\n"
  "qubit[2] q; bit[2] c;\n"
  "h q[0]; cx q[0], q[1];\n"
  "c = measure q;\n\n"
  "Part B — The result is the Bell state (Phi-plus):\n"
  "|Phi+> = (|00> + |11>) / sqrt(2)\n"
  "Expected probabilities: 50% |00> and 50% |11>; |01> and |11> never occur ideally.\n"
  "The qubits are maximally entangled — measuring one determines the other with certainty.\n\n"
  "Part C — On real hardware a few percent of |01> and |10> counts appear. Award the mark where the candidate "
  "attributes this to hardware NOISE: gate infidelity, decoherence during the circuit, and readout/measurement "
  "error. These outcomes are forbidden in the ideal noiseless simulation."),
 ("Task 2", "A2",
  "Construct a quantum circuit that demonstrates the SUPERDENSE CODING protocol, in which two classical bits are "
  "transmitted by sending a single qubit of a pre-shared entangled pair. "
  "Part A — Build the shared Bell pair, then show the encoding operation Alice applies for each of the four "
  "messages 00, 01, 10 and 11. "
  "Part B — Build the decoding stage Bob applies and measure. "
  "Part C — Run all four encodings and paste the histograms, confirming each message decodes correctly. "
  "(Activity 7 — Superdense Coding Protocol.)",
  BOX_CAP,
  "Part A — Shared Bell pair, then Alice's encoding:\n"
  "qc = QuantumCircuit(2, 2)\n"
  "qc.h(0); qc.cx(0, 1)          # shared entangled pair\n"
  "# Alice encodes her 2-bit message on HER qubit (qubit 0) only:\n"
  "#   message 00 -> apply I  (do nothing)\n"
  "#   message 01 -> apply X  qc.x(0)\n"
  "#   message 10 -> apply Z  qc.z(0)\n"
  "#   message 11 -> apply ZX qc.z(0); qc.x(0)\n\n"
  "Part B — Bob decodes by reversing the entangling operation:\n"
  "qc.cx(0, 1)\n"
  "qc.h(0)\n"
  "qc.measure([0, 1], [0, 1])\n\n"
  "Part C — Expected results (each encoding decodes to its own message):\n"
  "I  -> 00 ;  X -> 01 ;  Z -> 10 ;  ZX -> 11\n"
  "Award the mark where the candidate states the key point: TWO classical bits were delivered by transmitting "
  "only ONE qubit, because the entangled pair was shared in advance. Note that superdense coding is the dual of "
  "teleportation."),
 ("Task 3", "A3",
  "Construct the standard circuit for QUANTUM TELEPORTATION to transfer an unknown qubit state from Alice to Bob. "
  "Part A — Build the three-qubit circuit: prepare an arbitrary state on q0, create the Bell pair between q1 and "
  "q2, perform Alice's Bell measurement on q0 and q1, and apply Bob's conditional corrections to q2. "
  "Part B — State which two classical bits are sent and which correction each triggers. "
  "Part C — Run the circuit and show that the state prepared on q0 is reconstructed on q2. "
  "(Activity 6 — Quantum Teleportation.)",
  BOX_CAP,
  "Part A — Teleportation circuit:\n"
  "import numpy as np\n"
  "from qiskit import QuantumCircuit\n"
  "qc = QuantumCircuit(3, 3)\n"
  "qc.ry(np.pi/4, 0)      # the unknown state |psi> to teleport, on q0\n"
  "qc.h(1); qc.cx(1, 2)   # entangled Bell pair shared between Alice (q1) and Bob (q2)\n"
  "qc.cx(0, 1); qc.h(0)   # Alice's Bell measurement basis change\n"
  "qc.measure([0, 1], [0, 1])\n"
  "with qc.if_test((1, 1)): qc.x(2)   # correction controlled by bit 1\n"
  "with qc.if_test((0, 1)): qc.z(2)   # correction controlled by bit 0\n"
  "qc.measure(2, 2)\n\n"
  "Part B — Alice sends the two classical measurement bits (b0 b1):\n"
  "  00 -> Bob applies I      01 -> Bob applies X\n"
  "  10 -> Bob applies Z      11 -> Bob applies ZX\n\n"
  "Part C — Bob's qubit q2 reproduces the amplitudes originally prepared on q0 (within hardware noise).\n"
  "Award the mark where the candidate notes that the original state on q0 is DESTROYED by the Bell measurement, "
  "so the no-cloning theorem is not violated, and that the two classical bits must travel by an ordinary channel, "
  "so teleportation does not transmit information faster than light."),
 ("Task 4", "A4",
  "Explain the MATHEMATICAL STEPS that prove the quantum teleportation protocol works — that is, show "
  "algebraically that Bob's qubit ends up in Alice's original unknown state after the corrections are applied. "
  "Work through the full state evolution using Dirac notation. "
  "(Activity 6 — Quantum Teleportation; Topic 1 — Dirac notation and tensor products.)",
  MATH_CAP,
  "Award the mark where the candidate works through the following algebra (notation may vary):\n\n"
  "1. Initial state. Alice's unknown qubit: |psi> = a|0> + b|1>, with |a|^2 + |b|^2 = 1.\n"
  "   Shared Bell pair: |Phi+>_12 = (|00> + |11>)/sqrt(2).\n"
  "   Total: |psi>_0 (x) |Phi+>_12 = (a|0> + b|1>) (x) (|00> + |11>)/sqrt(2).\n\n"
  "2. Expand:\n"
  "   = (1/sqrt(2)) [ a|000> + a|011> + b|100> + b|111> ].\n\n"
  "3. Apply CNOT (control q0, target q1):\n"
  "   = (1/sqrt(2)) [ a|000> + a|011> + b|110> + b|101> ].\n\n"
  "4. Apply Hadamard to q0, using H|0> = (|0>+|1>)/sqrt(2) and H|1> = (|0>-|1>)/sqrt(2):\n"
  "   = (1/2) [ |00>(a|0> + b|1>) + |01>(a|1> + b|0>)\n"
  "           + |10>(a|0> - b|1>) + |11>(a|1> - b|0>) ].\n\n"
  "5. Read off the four equally likely (probability 1/4) measurement outcomes on q0 q1 and Bob's resulting state:\n"
  "   00 -> a|0> + b|1>  = |psi>      -> apply I\n"
  "   01 -> a|1> + b|0>              -> apply X\n"
  "   10 -> a|0> - b|1>              -> apply Z\n"
  "   11 -> a|1> - b|0>              -> apply ZX\n\n"
  "6. Conclusion. After the correction indicated by the two classical bits, Bob holds exactly a|0> + b|1> = |psi> "
  "in every branch. Alice's copy was destroyed by the measurement, so no cloning occurred, and the amplitudes a "
  "and b were never learned by either party."),
 ("Task 5", "A5",
  "Construct the circuit for the DEUTSCH ALGORITHM to distinguish a constant function from a balanced function "
  "using only one oracle query. "
  "Part A — Build the two-qubit circuit including the initial state preparation and the final Hadamard. "
  "Part B — Give the oracle construction for all four possible functions (constant-0, constant-1, "
  "balanced-identity and balanced-negation). "
  "Part C — Run the circuit against each oracle and state how you read constant versus balanced from the "
  "measurement. (Activity 9 — Deutsch and Deutsch-Jozsa Algorithms.)",
  BOX_CAP,
  "Part A — Deutsch circuit:\n"
  "qc = QuantumCircuit(2, 1)\n"
  "qc.x(1)             # target qubit to |1>\n"
  "qc.h(0); qc.h(1)    # -> |+>|-> ; the |-> target enables phase kickback\n"
  "# ... oracle U_f here ...\n"
  "qc.h(0)             # interference step\n"
  "qc.measure(0, 0)\n\n"
  "Part B — The four oracles (|x>|y> -> |x>|y XOR f(x)>):\n"
  "  constant_0        : f(x) = 0      -> do nothing (identity)\n"
  "  constant_1        : f(x) = 1      -> qc.x(1)\n"
  "  balanced_identity : f(x) = x      -> qc.cx(0, 1)\n"
  "  balanced_negation : f(x) = NOT x  -> qc.cx(0, 1); qc.x(1)\n\n"
  "Part C — Reading the result from the measurement of qubit 0:\n"
  "  measure 0 -> the function is CONSTANT\n"
  "  measure 1 -> the function is BALANCED\n"
  "Both constant oracles yield 0 and both balanced oracles yield 1, using ONE oracle query where a classical "
  "algorithm needs TWO. Award the mark where the candidate names phase kickback as the mechanism."),
 ("Task 6", "A6",
  "Explain the MATHEMATICAL STEPS that prove the Deutsch algorithm — show algebraically why the measurement "
  "outcome distinguishes a constant function from a balanced one after a single query. "
  "(Activity 9 — Deutsch Algorithm; Topic 3 — Phase Kickback.)",
  MATH_CAP,
  "Award the mark where the candidate works through the following algebra (notation may vary):\n\n"
  "1. Initial state: |0>|1>.\n\n"
  "2. After Hadamards on both qubits:\n"
  "   |+>|-> = [(|0> + |1>)/sqrt(2)] (x) [(|0> - |1>)/sqrt(2)].\n\n"
  "3. Phase kickback. For the target in |->, the oracle acts as\n"
  "   U_f |x>|-> = (-1)^f(x) |x>|->.\n"
  "   The target qubit is unchanged; the phase (-1)^f(x) attaches to the input register.\n\n"
  "4. State of the input register after the oracle:\n"
  "   (1/sqrt(2)) [ (-1)^f(0)|0> + (-1)^f(1)|1> ].\n"
  "   Factor out the global phase (-1)^f(0):\n"
  "   = (-1)^f(0) (1/sqrt(2)) [ |0> + (-1)^(f(0) XOR f(1)) |1> ].\n\n"
  "5. Two cases:\n"
  "   CONSTANT, f(0) = f(1), so f(0) XOR f(1) = 0 -> state is |+> (up to global phase).\n"
  "   BALANCED, f(0) != f(1), so f(0) XOR f(1) = 1 -> state is |-> (up to global phase).\n\n"
  "6. Final Hadamard converts the phase difference into a measurable amplitude:\n"
  "   H|+> = |0>   and   H|-> = |1>.\n\n"
  "7. Conclusion. Measuring the input qubit gives 0 with certainty for a constant function and 1 with certainty "
  "for a balanced function, after ONE oracle query. The global phase (-1)^f(0) is unobservable and does not "
  "affect the outcome."),
 ("Task 7", "A7",
  "Construct a quantum circuit for SINGLE-QUBIT BIT-FLIP ERROR CORRECTION and explain the mathematics behind it. "
  "Part A — Build the circuit: encode one logical qubit into three physical qubits, inject an X error on one of "
  "them, compute the syndrome onto two ancilla qubits, and measure only the ancillas. "
  "Part B — Give the full syndrome table and the correction each syndrome triggers. "
  "Part C — Explain why the syndrome is measured instead of the data qubits, and why this does not violate the "
  "no-cloning theorem. (Activity 17 — Bit-Flip and Phase-Flip Error Correction Codes.)",
  BOX_CAP,
  "Part A — Bit-flip code circuit (3 data qubits + 2 ancillas):\n"
  "qc = QuantumCircuit(5, 2)\n"
  "# Encode: |psi> -> a|000> + b|111>\n"
  "qc.cx(0, 1); qc.cx(0, 2)\n"
  "# Inject an error (simulate the environment flipping qubit 1):\n"
  "qc.x(1)\n"
  "# Syndrome extraction — parity of qubit pairs onto the ancillas:\n"
  "qc.cx(0, 3); qc.cx(1, 3)     # ancilla 3 = parity of q0,q1\n"
  "qc.cx(1, 4); qc.cx(2, 4)     # ancilla 4 = parity of q1,q2\n"
  "qc.measure([3, 4], [0, 1])   # measure ONLY the ancillas\n\n"
  "Part B — Syndrome table (ancilla3, ancilla4) -> correction:\n"
  "  00 -> no error            -> do nothing\n"
  "  10 -> error on qubit 0    -> apply X to q0\n"
  "  11 -> error on qubit 1    -> apply X to q1\n"
  "  01 -> error on qubit 2    -> apply X to q2\n\n"
  "Part C — Award the mark where the candidate explains:\n"
  "The encoded state is a|000> + b|111>. The syndrome measures the PARITY between qubit pairs, which reveals "
  "WHICH qubit flipped without revealing anything about the amplitudes a and b. Measuring the data qubits "
  "directly would collapse the superposition and destroy the logical information.\n"
  "No-cloning is not violated because the encoding does NOT create three copies of |psi>: it produces the "
  "entangled state a|000> + b|111>, which is not |psi>|psi>|psi>. The code corrects a single X error; the "
  "phase-flip code is the same construction conjugated by Hadamards, which turns Z errors into X errors."),
]

# ---------------------------------------------------------------- doc helpers
def base_doc():
    doc = Document()
    n = doc.styles["Normal"]; n.font.name = "Arial"; n.font.size = Pt(11)
    return doc

def para(doc, text, size=11, bold=False, italic=False, color=None, after=6, before=0, align=None):
    p = doc.add_paragraph(); r = p.add_run(text)
    r.font.size = Pt(size); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    if align is not None: p.alignment = align
    return p

def heading(doc, text, size=13):
    para(doc, text, size=size, bold=True, color=BRAND, after=6, before=8)

def answer_box(doc, lines=None, code=None, height_pt=90):
    """1x1 bordered box. `lines` → bullet-style model answer; `code` → monospace
    code/YAML/command block (indentation preserved); neither → empty answer space."""
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    cell.paragraphs[0].text = ""
    if code:
        run = cell.paragraphs[0].add_run("Suggestive answers (not exhaustive):")
        run.bold = True; run.font.size = Pt(10.5)
        for ln in code.split("\n"):
            b = cell.add_paragraph(style=None)
            b.paragraph_format.space_after = Pt(0); b.paragraph_format.space_before = Pt(0)
            rr = b.add_run(ln if ln else " ")
            rr.font.name = "Consolas"; rr.font.size = Pt(9)
            rr._element.rPr.rFonts.set(qn('w:cs'), "Consolas")
            wt = rr._element.find(qn('w:t'))
            if wt is not None: wt.set(qn('xml:space'), 'preserve')
    elif lines:
        run = cell.paragraphs[0].add_run("Suggestive answers (not exhaustive):")
        run.bold = True; run.font.size = Pt(10.5)
        for ln in lines:
            b = cell.add_paragraph(style=None); b.paragraph_format.left_indent = Inches(0.15)
            rr = b.add_run("•  " + ln); rr.font.size = Pt(10.5)
    else:
        # empty answer space
        tr = t.rows[0]._tr
        trPr = tr.get_or_add_trPr(); trh = OxmlElement('w:trHeight')
        trh.set(qn('w:val'), str(int(height_pt*20))); trh.set(qn('w:hRule'), 'atLeast'); trPr.append(trh)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

FILL_GAP = 6    # extra space below each fill-in line (paired with double line spacing for writing room)

def candidate_block(doc):
    heading(doc, "Trainee Information")
    for label in ["Trainee Name (as per NRIC): ______________________________________",
                  "Last 3 digits and alphabet of NRIC/FIN: ____________________",
                  "Date: ____________________"]:
        p = para(doc, label, size=11, after=FILL_GAP)
        p.paragraph_format.line_spacing = 2.0

# Assessment briefing (from the course slides — "Briefing for Assessment").
BRIEFING = [
    "Place phones and other materials under the table or on the floor.",
    "No photos or recording of assessment scripts.",
    "No discussion during the assessment.",
    "Use a black/blue pen for hard-copy assessments.",
    "No liquid paper / correction tape.",
    "Scripts are collected when time is up.",
]

LMS_URL = "https://lms-tms.tertiaryinfotech.com/"

def add_hyperlink(p, url, text):
    """Add a real clickable Word hyperlink (blue, underlined) to paragraph p."""
    r_id = p.part.relate_to(
        url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)
    link = OxmlElement("w:hyperlink"); link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r"); rPr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "22"); rPr.append(sz)  # 11pt
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1"); rPr.append(color)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rPr.append(u)
    run.append(rPr)
    t = OxmlElement("w:t"); t.text = text; run.append(t)
    link.append(run); p._p.append(link)
    return link

def instructions(doc, minutes_text):
    heading(doc, "Instructions to Candidate")
    # None marks the upload instruction, which carries a clickable LMS hyperlink.
    items = [
        "This is an individual exercise.",
        "This is an open-book assessment.",
        f"A total of {minutes_text} is given to complete this assessment.",
        None,
    ] + BRIEFING
    for i, s in enumerate(items, 1):
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
        if s is None:
            p.add_run(f"{i}.  Complete your answers on the document provided and "
                      "upload the completed answers to the LMS at ").font.size = Pt(11)
            add_hyperlink(p, LMS_URL, LMS_URL)
            p.add_run(".").font.size = Pt(11)
        else:
            p.add_run(f"{i}.  {s}").font.size = Pt(11)

def grading(doc, what):
    heading(doc, "Grading")
    para(doc, what, size=11, after=12)
    for ln in ["Grade: _______  (C / NYC)",
               "Assessor Name: __________________________   Assessor NRIC: ________________",
               "Date: ________________________                    Signature: ____________________"]:
        p = para(doc, ln, size=11, after=FILL_GAP)
        p.paragraph_format.line_spacing = 2.0

def finish(doc, path):
    prodoc.add_page_numbers(doc); prodoc.enable_update_fields(doc)
    doc.save(path); print("  saved:", os.path.basename(path))

# ---------------------------------------------------------------- builders
def build_wa(answers):
    doc = base_doc()
    kind = "Written Assessment (SAQ) — Answer Key" if answers else "Written Assessment (SAQ)"
    prodoc.add_cover_page(doc, kind, TITLE, A_VER if answers else Q_VER,
                          org_logo=ORG_LOGO, course_logo=COURSE_LOGO)
    para(doc, TITLE, size=15, bold=True, color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, "Answers to Written Assessment (SAQ)" if answers else "Written Assessment (SAQ)",
         size=13, bold=True, color=BRAND, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, f"Course Code: {COURSE_CODE}", size=11, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
    if not answers:
        # Page 2 — candidate information, instructions and grading; questions begin on the next page.
        candidate_block(doc); instructions(doc, "1 hour")
        grading(doc, "Candidate has answered all written questions and demonstrated the underpinning "
                     "knowledge required for the course learning outcomes.")
        page_break(doc)
    para(doc, "Short-Answer Questions (Knowledge)", size=13, bold=True, color=BRAND, after=4)
    para(doc, "Answer all questions in your own words. Each question tests underpinning knowledge covered in the "
              "course slides.", size=10.5, italic=True, color=GREY, after=8)
    # Pagination is EXPLICIT — two questions to a page on the paper, one model answer to a
    # page in the key. Do not swap this for Word's keepNext/cantSplit: Word pushes an
    # oversized box to the next page, but Google Docs draws the border anyway and prints the
    # question text and the page footer straight THROUGH it. See SKILL.md → Pagination.
    per_page = 1 if answers else 2
    for i, (crit, ctx, q, pts) in enumerate(WRITTEN, 1):
        para(doc, f"Question {i}:", size=11.5, bold=True, after=2, before=6)
        para(doc, ctx, size=11, after=3)
        para(doc, f"{q}  ({crit})", size=11, bold=True, after=4)
        answer_box(doc, lines=pts if answers else None)
        if i % per_page == 0 and i < len(WRITTEN):
            page_break(doc)
    suffix = A_VER if answers else Q_VER
    name = (f"Answer to WA (SAQ) - {TITLE} - {suffix}.docx" if answers
            else f"WA (SAQ) - {TITLE} - {suffix}.docx")
    finish(doc, os.path.join(OUT, name))

def build_pp(answers):
    doc = base_doc()
    kind = "Practical Performance (PP) — Answer Key" if answers else "Practical Performance (PP)"
    prodoc.add_cover_page(doc, kind, TITLE, A_VER if answers else Q_VER,
                          org_logo=ORG_LOGO, course_logo=COURSE_LOGO)
    para(doc, TITLE, size=15, bold=True, color=DARK, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, "Answers to Practical Performance Assessment" if answers else "Practical Performance Assessment",
         size=13, bold=True, color=BRAND, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, f"Course Code: {COURSE_CODE}", size=11, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)
    if not answers:
        # Page 2 — candidate information, instructions and grading; the problem begins on the next page.
        candidate_block(doc); instructions(doc, "1 hour")
        grading(doc, "Candidate has successfully completed all PP tasks and can explain the overall "
                     "functions and features used to achieve them.")
        page_break(doc)
    para(doc, "Practical Problem", size=13, bold=True, color=BRAND, after=4)
    para(doc, "Scenario", size=11.5, bold=True, after=2)
    para(doc, SCENARIO, size=11, after=8)
    # Practical tasks are long and their boxes are tall, so they get a page each — on the
    # paper AND in the key. Same rule as the WA: the page break is ours, not the renderer's.
    for i, (label, crit, prompt, cap, pts) in enumerate(PRACTICAL, 1):
        para(doc, f"{label} ({crit}):", size=11.5, bold=True, after=2, before=6)
        para(doc, prompt, size=11, after=3)
        para(doc, cap, size=10.5, italic=True, color=GREY, after=4)
        answer_box(doc, code=pts if answers else None, height_pt=150)
        if i < len(PRACTICAL):
            page_break(doc)
    suffix = A_VER if answers else Q_VER
    name = (f"Answer to PP Assessment - {TITLE} - {suffix}.docx" if answers
            else f"PP Assessment - {TITLE} - {suffix}.docx")
    finish(doc, os.path.join(OUT, name))

if __name__ == "__main__":
    print("Building WSQ assessment set…")
    build_wa(answers=False); build_wa(answers=True)
    build_pp(answers=False); build_pp(answers=True)
    print(f"Done. WA: {len(WRITTEN)} questions · PP: {len(PRACTICAL)} tasks.")
