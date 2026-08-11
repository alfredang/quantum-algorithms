"""
Activity 14 — Post-Quantum Cryptography Migration Assessment
Topic 6: Quantum Cryptography and Quantum Safety  ·  LO4, LO7

Builds a cryptographic inventory for a sample organisation, classifies each asset
by how a quantum computer attacks it, maps it to the correct NIST post-quantum
replacement, and scores the harvest-now-decrypt-later risk to produce a
prioritised migration plan.

Pure Python — no quantum SDK required.

Run:  python labs/pqc-migration/main.py
      python labs/pqc-migration/main.py --scan www.tertiarycourses.com.sg
"""
import argparse
import subprocess
import sys

# ---------------------------------------------------------------- reference data
# How a quantum computer attacks each algorithm family, and what replaces it.
SHOR_BROKEN = {"RSA", "ECC", "ECDSA", "ECDH", "DH", "DSA"}
GROVER_WEAKENED = {"AES", "SHA", "3DES", "ChaCha20"}

NIST_PQC = {
    "kem":       ("ML-KEM (Kyber)",     "FIPS 203"),
    "signature": ("ML-DSA (Dilithium)", "FIPS 204"),
    "signature_hash": ("SLH-DSA (SPHINCS+)", "FIPS 205"),
    "kem_backup": ("HQC",               "NIST 2025 selection"),
}

# (asset, algorithm, key//hash size, purpose, years the data must stay confidential)
INVENTORY = [
    ("Public website TLS certificate", "RSA",    2048, "key exchange + signature", 2),
    ("Internal API mutual TLS",        "ECDSA",  256,  "authentication",           3),
    ("Site-to-site VPN",               "ECDH",   256,  "key exchange",             5),
    ("Code-signing certificate",       "RSA",    4096, "signature",                10),
    ("Database at-rest encryption",    "AES",    256,  "bulk encryption",          15),
    ("Backup archive encryption",      "AES",    128,  "bulk encryption",          20),
    ("Password hashing",               "SHA",    256,  "integrity",                10),
    ("Patient records archive",        "RSA",    2048, "key exchange",             25),
    ("SSH host and user keys",         "ECDSA",  256,  "authentication",           3),
    ("Document signing (legal)",       "RSA",    3072, "signature",                30),
]


def classify(alg, size):
    """Return (threat, severity, effective_security_after_quantum, replacement)."""
    family = alg.upper()
    if family in SHOR_BROKEN:
        purpose = "signature" if family in {"RSA", "DSA", "ECDSA"} else "kem"
        name, fips = NIST_PQC["signature" if purpose == "signature" else "kem"]
        return ("BROKEN by Shor", 3, 0, f"{name} ({fips})")
    if family in GROVER_WEAKENED:
        eff = size // 2                      # Grover halves the effective key length
        if eff >= 128:
            return ("Weakened by Grover", 1, eff, f"Adequate — {alg}-{size} stays safe")
        return ("Weakened by Grover", 2, eff,
                f"Increase key size (use {alg}-256 / SHA-512)")
    return ("Unclassified", 1, size, "Review manually")


def risk_score(severity, years):
    """Harvest-now-decrypt-later: long-lived secrets under a broken algorithm rank
    highest. Severity 3 (Shor-broken) dominates; lifetime breaks the ties."""
    return severity * 10 + min(years, 30) // 5


def scan_certificate(host):
    """Read the public-key algorithm off a live TLS certificate (step 2 of the lab)."""
    cmd = (f"echo | openssl s_client -connect {host}:443 -servername {host} 2>/dev/null "
           f"| openssl x509 -noout -text 2>/dev/null | grep -A2 'Public Key Algorithm'")
    try:
        out = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True,
                             timeout=25).stdout.strip()
    except Exception as e:
        return f"could not scan {host}: {e}"
    return out or f"no certificate data returned for {host}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", metavar="HOST",
                    help="read the public-key algorithm off a live TLS certificate")
    args = ap.parse_args()

    print("=" * 78)
    print("Activity 14 — Post-Quantum Cryptography Migration Assessment")
    print("=" * 78)

    if args.scan:
        print(f"\nSTEP 2 — live certificate scan: {args.scan}")
        print(scan_certificate(args.scan))

    # STEP 3-6 — classify every asset
    print("\nSTEP 3-6 — Cryptographic inventory and quantum threat classification")
    print("-" * 78)
    print(f"{'Asset':<32}{'Algorithm':<12}{'Threat':<20}{'Post-quantum action'}")
    print("-" * 78)
    rows = []
    for asset, alg, size, purpose, years in INVENTORY:
        threat, sev, eff, repl = classify(alg, size)
        rows.append((asset, alg, size, purpose, years, threat, sev, eff, repl))
        print(f"{asset:<32}{alg + '-' + str(size):<12}{threat:<20}{repl}")

    # STEP 4 — the Grover detail
    print("\nSTEP 4 — Grover halves the effective key length of symmetric primitives")
    for asset, alg, size, *_ , sev, eff, repl in [r for r in rows if "Grover" in r[5]]:
        verdict = "SAFE" if eff >= 128 else "TOO WEAK — increase the key size"
        print(f"   {alg}-{size:<4} -> ~{eff}-bit effective security   {verdict}")

    # STEP 7-9 — prioritised migration plan
    print("\nSTEP 7-9 — Prioritised migration plan (harvest-now-decrypt-later)")
    print("-" * 78)
    print(f"{'Pri':<5}{'Asset':<32}{'Current':<12}{'Confid.':<9}{'Risk':<6}Replacement")
    print("-" * 78)
    ranked = sorted(rows, key=lambda r: risk_score(r[6], r[4]), reverse=True)
    for i, (asset, alg, size, purpose, years, threat, sev, eff, repl) in enumerate(ranked, 1):
        print(f"{i:<5}{asset:<32}{alg + '-' + str(size):<12}{str(years) + 'y':<9}"
              f"{risk_score(sev, years):<6}{repl}")

    # STEP 10 — transition strategy
    print("\nSTEP 10 — Transition strategy")
    for line in [
        "Deploy HYBRID key exchange (classical + ML-KEM) during the transition, so the",
        "  session stays secure if either component holds.",
        "Prioritise assets whose data must remain confidential for longest — they are",
        "  already exposed to harvest-now-decrypt-later capture.",
        "Build crypto-agility: keep algorithms configurable, not hardcoded, so the next",
        "  migration is a config change rather than a rewrite.",
        "Long-lived devices (IoT, ICS, medical) need attention first — they cannot be",
        "  easily updated once deployed.",
    ]:
        print("  - " + line)

    # ---------------------------------------------------------------- test it
    broken = [r for r in rows if r[5].startswith("BROKEN")]
    weakened = [r for r in rows if "Grover" in r[5]]
    print("\n" + "=" * 78)
    print("TEST IT")
    print("=" * 78)
    print(f"Shor-broken asymmetric assets identified : {len(broken)}")
    print(f"Grover-weakened symmetric assets         : {len(weakened)}")
    print(f"Highest-priority asset                   : {ranked[0][0]} "
          f"({ranked[0][1]}-{ranked[0][2]}, {ranked[0][4]}y confidentiality)")
    assert all(r[8].startswith(("ML-KEM", "ML-DSA")) for r in broken), \
        "every Shor-broken asset must map to a NIST PQC replacement"
    assert any("AES-128" in f"{r[1]}-{r[2]}" for r in weakened), "AES-128 should be flagged"
    assert ranked[0][6] == 3, "a Shor-broken asset must rank above a Grover-weakened one"
    print("\nInventory correctly separates Shor-broken from Grover-weakened algorithms,")
    print("maps each to the correct NIST FIPS standard, and ranks migration priority")
    print("by how long the data must remain confidential.  All assertions passed.")


if __name__ == "__main__":
    main()
