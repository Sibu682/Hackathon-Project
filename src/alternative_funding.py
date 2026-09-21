"""
Alternative Financial Aid module — strict eligibility matching.

Each partner has defined eligibility rules. A partner is only shown
when the student passes ALL applicable filters.
"""

from __future__ import annotations

from typing import Any

from data import ALTERNATIVE_FUNDING_PARTNERS


def _student_qualifies(partner: dict[str, Any], student: dict[str, Any]) -> bool:
    """Return True only if the student meets this partner's eligibility criteria."""
    fs = student["funding_status"]
    income = student["financial_profile"].get("household_income", 0)
    is_nsfas_funded = fs.get("nsfas_funded", False)
    is_defunded = fs.get("defunded", False)
    outstanding = fs.get("outstanding_balance", 0)

    # ── ISFAP (AF001) — missing middle ────────────────────────────────────
    if partner["id"] == "AF001":
        # Must NOT be currently NSFAS-funded (unless defunded)
        if is_nsfas_funded and not is_defunded:
            return False
        # Income ceiling
        threshold = partner.get("income_threshold") or 600_000
        if income > threshold:
            return False

    # ── UNISA SFAF (AF002) — emergency fund ──────────────────────────────
    elif partner["id"] == "AF002":
        # Only relevant when there is a financial need (outstanding balance or low income)
        income_threshold = partner.get("income_threshold") or 350_000
        has_financial_distress = outstanding > 0 or income <= income_threshold
        if not has_financial_distress:
            return False

    # ── Fundi Loan (AF003) — always available ────────────────────────────
    # No additional filter — available to any registered student

    return True


def get_matched_partners(student: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only the alternative funding partners the student qualifies for."""
    return [p for p in ALTERNATIVE_FUNDING_PARTNERS if _student_qualifies(p, student)]
