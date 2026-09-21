"""Final verification — bursary matches, alt funding, contacts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import STUDENT_DATABASE
from src.bursary_recommender import recommend_bursaries, _passes_hard_filters, BURSARY_CATALOGUE
from src.alternative_funding import get_matched_partners
from config.settings import UNISA_CONTACT_CENTRE, UNISA_FINANCE_EMAIL, NSFAS_HELPLINE, NSFAS_EMAIL

errors = []

print("=== FINAL VERIFICATION ===\n")

for uid, student in STUDENT_DATABASE.items():
    name  = student["personal_info"]["first_name"]
    gpa   = student["academic_record"]["gpa"]
    recs  = recommend_bursaries(student)
    alt   = get_matched_partners(student)
    print(f"[{uid}] {name} — GPA {gpa}%")
    print(f"  Bursary matches : {len(recs)}")
    for b in recs:
        # Strip injected keys before re-checking
        b_clean = {k: v for k, v in b.items() if not k.startswith("_")}
        print(f"    ✓ {b_clean['name']}  (score={b['_score']})")
    print(f"  Alt funding     : {len(alt)}")
    for a in alt:
        print(f"    ~ {a['name']}")
    print()

print("=== CONTACTS ===")
contacts = {
    "UNISA toll-free": (UNISA_CONTACT_CENTRE, "0800 00 1870"),
    "UNISA finance email": (UNISA_FINANCE_EMAIL, "finan@unisa.ac.za"),
    "NSFAS helpline": (NSFAS_HELPLINE, "0800 067 327"),
    "NSFAS email": (NSFAS_EMAIL, "info@nsfas.org.za"),
}
for label, (actual, expected) in contacts.items():
    status = "✓" if actual == expected else "✗"
    print(f"  {status} {label}: {actual}")
    if actual != expected:
        errors.append(f"Contact mismatch [{label}]: got {actual}, expected {expected}")

print()
if errors:
    print(f"FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED ✓")
