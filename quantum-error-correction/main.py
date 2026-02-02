"""
Quantum Error Correction

This folder contains implementations of fundamental quantum error correction codes:

1. bit-flip-code/ - 3-qubit bit-flip code
   - Protects against single X (bit-flip) errors
   - Encoding: |0⟩ → |000⟩, |1⟩ → |111⟩

2. phase-flip-code/ - 3-qubit phase-flip code
   - Protects against single Z (phase-flip) errors
   - Encoding: |0⟩ → |+++⟩, |1⟩ → |---⟩

To run either code:
    cd bit-flip-code && python main.py
    cd phase-flip-code && python main.py

Both implementations run on IBM Quantum hardware using your saved credentials.
"""

print(__doc__)
print("Please run the specific code implementations:")
print("  - error-correction/bit-flip-code/main.py")
print("  - error-correction/phase-flip-code/main.py")
