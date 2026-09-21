"""Verify bursary eligibility filtering and contact data."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data import STUDENT_DATABASE
from src.bursary_recommender import recommend_bursaries, _passes_hard_filters, BURSARY_CATALOGUE
from src.alternative_funding import get_matched_partners
from config.settings import (
    UNISA_CONTACT_CENTRE, UNISA_FINANCE_EMAIL,
    NSFAS_HELPLINE, NSFAS_EMAIL
)

errors = []

print("=" * 60)
print("BURSARY ELIGIBILITY VERIFICATION")
print("=" * 60)

for student_id, student in STUDENT_DATABASE.items():
    name = f"{student['personal_info']['first_name']} {student['personal_info']['last_name']}"
    gpa  = student['academic_record']['gpa']
    income = student['financial_profile']['household_income']
    recs = recommend_bursaries(student)

    print(f"\n{name} ({student_id}) — GPA {gpa}% — Income R{income:,}")
    print(f"  Bursaries matched: {len(recs)}")

    for b in recs:
        # Double-check every returned bursary passes hard filters
        passes, failures = _passes_hard_filters(b, student)
        if not passes:
            errors.append(
                f"  ERROR: '{b['name']}' shown for {name} but FAILS: {failures}"
            )
            print(f"  ✗ {b['name']} — FAILS hard filter!")
        else:
            print(f"  ✓ {b['name']} (score={b['_score']})")

    # Also verify NO ineligible bursary slipped through
    for b in BURSARY_CATALOGUE:
        b_id = b['id']
        returned_ids = {r['id'] for r in recs}
        passes, _ = _passes_hard_filters(b, student)
        if passes and b_id not in returned_ids:
            errors.append(
                f"  MISS: '{b['name']}' PASSES filters for {name} but was NOT returned"
            )

    alt = get_matched_partners(student)
    print(f"  Alt funding matched: {len(alt)} — {[p['name'][:30] for p in alt]}")

print("\n" + "=" * 60)
print("CONTACT DATA VERIFICATION")
print("=" * 60)
print(f"  UNISA contact centre: {UNISA_CONTACT_CENTRE}")
print(f"  UNISA finance email:  {UNISA_FINANCE_EMAIL}")
print(f"  NSFAS helpline:       {NSFAS_HELPLINE}")
print(f"  NSFAS email:          {NSFAS_EMAIL}")

assert UNISA_CONTACT_CENTRE == "0800 00 1870", f"Wrong UNISA number: {UNISA_CONTACT_CENTRE}"
assert UNISA_FINANCE_EMAIL  == "finan@unisa.ac.za", f"Wrong UNISA email: {UNISA_FINANCE_EMAIL}"
assert NSFAS_HELPLINE       == "0800 067 327", f"Wrong NSFAS number: {NSFAS_HELPLINE}"
assert NSFAS_EMAIL          == "info@nsfas.org.za", f"Wrong NSFAS email: {NSFAS_EMAIL}"
print("  All contact details ✓")

print("\n" + "=" * 60)
if errors:
    print(f"FAILED — {len(errors)} error(s):")
    for e in errors: print(e)
    sys.exit(1)
else:
    print("ALL CHECKS PASSED ✓")
