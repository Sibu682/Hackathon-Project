"""Quick smoke test — run with: python3 smoke_test.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data import STUDENT_DATABASE, BURSARY_CATALOGUE, ALTERNATIVE_FUNDING_PARTNERS
from config.settings import APP_NAME, APP_VERSION
from src.auth import authenticate
from src.ai_agent import _rule_based_assessment
from src.bursary_recommender import recommend_bursaries
from src.alternative_funding import _match_partners

errors = []

# 1. Dataset integrity
assert len(STUDENT_DATABASE) == 4, "Expected 4 students in database"
assert len(BURSARY_CATALOGUE) == 10, "Expected 10 bursaries"
assert len(ALTERNATIVE_FUNDING_PARTNERS) == 4, "Expected 4 alt-funding partners"
print("✓  Dataset loaded (4 students, 10 bursaries, 4 alt-funding partners)")

# 2. Rule-based assessment for all 4 scenarios
expected_actions = {
    "thabo.mokoena":  "apply_for_nsfas",
    "lerato.dlamini": "contact_student_finance",
    "naledi.sithole": "view_dashboard",
    "sipho.nkosi":    "appeal_defunding",
}
for username, expected in expected_actions.items():
    student = STUDENT_DATABASE[username]
    result = _rule_based_assessment(student)
    action = result["recommended_action"]
    status = "✓" if action == expected else "✗"
    print(f"{status}  {username:<30} → {action}  (expected: {expected})")
    if action != expected:
        errors.append(f"Wrong action for {username}: got {action}")

# 3. Authentication
s = authenticate("thabo.mokoena", "Pass@1234")
assert s is not None, "Auth should succeed"
print("✓  authenticate() with correct credentials works")

s_fail = authenticate("thabo.mokoena", "wrongpassword")
assert s_fail is None, "Auth should fail with wrong password"
print("✓  authenticate() with wrong credentials returns None")

# 4. Bursary recommendations
for username in STUDENT_DATABASE:
    recs = recommend_bursaries(STUDENT_DATABASE[username])
    print(f"✓  {username:<30} → {len(recs)} bursary recommendation(s)")

# 5. Alternative funding matching
for username in STUDENT_DATABASE:
    partners = _match_partners(STUDENT_DATABASE[username])
    print(f"✓  {username:<30} → {len(partners)} alternative funding match(es)")

# 6. Config
assert APP_NAME, "APP_NAME missing"
assert APP_VERSION, "APP_VERSION missing"
print(f"✓  Config loaded: {APP_NAME} v{APP_VERSION}")

if errors:
    print(f"\n✗  {len(errors)} error(s):")
    for e in errors:
        print(f"   - {e}")
    sys.exit(1)
else:
    print("\n✓  All smoke tests passed.")
