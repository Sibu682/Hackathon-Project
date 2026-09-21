"""
Personalised Bursary Recommendation Engine.

STRICT eligibility filtering: a bursary is only shown if the student
passes ALL hard filters. Soft factors (financial need, GPA headroom)
contribute to the relevance score but never exclude an eligible bursary.

Hard filters (student MUST pass all):
  1. Field of study — at least one of the student's unfunded quals must
     match the bursary's fields_of_study list.
  2. NQF level     — at least one of the student's unfunded quals must
     match the bursary's nqf_levels list.
  3. GPA           — student GPA must be ≥ bursary's min_gpa.
  4. Nationality   — student nationality must be in the bursary's list.
  5. Year of study — student year_of_study must be ≥ bursary's min_year_of_study.
  6. Income ceiling — if financial_need_required is True, student household
     income must be ≤ income_ceiling (default R350 000 if not specified).
  7. Qualification type — bursary must be "undergraduate" or "both".
"""

from __future__ import annotations

from typing import Any

from data import BURSARY_CATALOGUE

# ---------------------------------------------------------------------------
# Field-of-study keyword mapping
# ---------------------------------------------------------------------------

_FIELD_KEYWORDS: dict[str, list[str]] = {
    "Commerce":               ["commerce"],
    "Information Technology": ["information technology", "bsc it", "bscit"],
    "Humanities":             ["political science", "arts", "humanities"],
    "Law":                    ["law", "llb"],
    "Business Administration":["business administration", "diploma in business"],
    "Science":                ["science"],
    "Accounting":             ["accounting"],
    "Finance":                ["finance"],
    "Engineering":            ["engineering"],
    "Social Work":            ["social work"],
    "Psychology":             ["psychology"],
}


def _fields_from_qual(qual: dict[str, Any]) -> set[str]:
    """Return matching field-of-study labels for a single qualification."""
    name = qual["qualification_name"].lower()
    matched: set[str] = set()
    for label, keywords in _FIELD_KEYWORDS.items():
        if any(kw in name for kw in keywords):
            matched.add(label)
    return matched


def _get_all_student_fields(student: dict[str, Any]) -> set[str]:
    fields: set[str] = set()
    for qual in student["academic_record"].get("registered_qualifications", []):
        fields |= _fields_from_qual(qual)
    return fields


def _get_unfunded_quals(student: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of registered qualifications that are NOT NSFAS funded."""
    fs = student["funding_status"]
    unfunded_codes = fs.get("unfunded_qualifications", [])
    result = []
    for qual in student["academic_record"].get("registered_qualifications", []):
        code = qual["qualification_code"]
        per_qual_funded = qual.get("nsfas_funded", None)
        if unfunded_codes and code in unfunded_codes:
            result.append(qual)
        elif per_qual_funded is False:
            result.append(qual)
        elif not fs.get("nsfas_funded", False):
            result.append(qual)
    return result


def _unfunded_fields(student: dict[str, Any]) -> set[str]:
    fields: set[str] = set()
    for qual in _get_unfunded_quals(student):
        fields |= _fields_from_qual(qual)
    return fields


def _unfunded_nqf_levels(student: dict[str, Any]) -> set[int]:
    levels: set[int] = set()
    for qual in _get_unfunded_quals(student):
        code = qual["qualification_code"]
        # Look up NQF level from the catalogue if available
        from data import QUALIFICATIONS_CATALOGUE
        cat_entry = QUALIFICATIONS_CATALOGUE.get(code)
        if cat_entry:
            levels.add(cat_entry["nqf_level"])
    return levels


# ---------------------------------------------------------------------------
# Hard-filter + scoring
# ---------------------------------------------------------------------------

_DEFAULT_INCOME_CEILING = 350_000  # NSFAS / financial-need threshold (ZAR)


def _passes_hard_filters(
    bursary: dict[str, Any],
    student: dict[str, Any],
    scope_fields: set[str] | None = None,
    scope_nqf: set[int] | None = None,
) -> tuple[bool, list[str]]:
    """
    Apply all hard eligibility filters.

    scope_fields / scope_nqf: pre-resolved field and NQF sets from the caller.
    If not supplied they are derived from the student's unfunded qualifications.
    """
    failures: list[str] = []

    gpa = student["academic_record"].get("gpa", 0.0)
    income = student["financial_profile"].get("household_income", 999_999)
    nationality = student["personal_info"].get("nationality", "")
    year_of_study = student["academic_record"].get("year_of_study", 1)

    u_fields = scope_fields if scope_fields is not None else _unfunded_fields(student)
    u_nqf    = scope_nqf    if scope_nqf    is not None else _unfunded_nqf_levels(student)

    b_fields = set(bursary["fields_of_study"])
    b_nqf = set(bursary.get("nqf_levels", []))

    # 1. Qualification type
    q_type = bursary.get("qualification_type", "undergraduate")
    if q_type == "postgraduate":
        failures.append("Postgraduate-only bursary — not applicable to undergraduate students.")

    # 2. Field of study — at least one unfunded field must match
    if "All" not in b_fields and not (u_fields & b_fields):
        failures.append(
            f"Field of study mismatch. Bursary covers: {', '.join(sorted(b_fields))}. "
            f"Your unfunded qualification(s): {', '.join(sorted(u_fields)) or 'none'}."
        )

    # 3. NQF level — at least one unfunded qual NQF must match
    if b_nqf and not (u_nqf & b_nqf):
        failures.append(
            f"NQF level mismatch. Bursary covers NQF {', '.join(str(n) for n in sorted(b_nqf))}. "
            f"Your qualification NQF: {', '.join(str(n) for n in sorted(u_nqf)) or 'unknown'}."
        )

    # 4. Minimum GPA
    min_gpa = bursary.get("min_gpa", 0.0)
    if gpa < min_gpa:
        failures.append(
            f"GPA requirement not met. Required: {min_gpa}%. Your GPA: {gpa}%."
        )

    # 5. Nationality
    allowed_nationalities = bursary.get("nationality", ["South African"])
    if nationality not in allowed_nationalities and "Other" not in allowed_nationalities:
        failures.append(
            f"Nationality not eligible. Bursary requires: {', '.join(allowed_nationalities)}."
        )

    # 6. Year of study
    min_year = bursary.get("min_year_of_study", 1)
    if year_of_study < min_year:
        failures.append(
            f"Year of study requirement not met. "
            f"Minimum year required: {min_year}. Your current year: {year_of_study}."
        )

    # 7. Financial need / income ceiling
    if bursary.get("financial_need_required", False):
        ceiling = bursary.get("income_ceiling") or _DEFAULT_INCOME_CEILING
        if income > ceiling:
            failures.append(
                f"Household income R{income:,} exceeds the financial need ceiling "
                f"of R{ceiling:,} for this bursary."
            )

    return (len(failures) == 0), failures


def _score_bursary(
    bursary: dict[str, Any],
    student: dict[str, Any],
    scope_fields: set[str] | None = None,
) -> tuple[int, list[str]]:
    """Score a bursary that has already passed all hard filters."""
    score = 0
    matched: list[str] = []

    gpa = student["academic_record"].get("gpa", 0.0)
    income = student["financial_profile"].get("household_income", 999_999)

    u_fields = scope_fields if scope_fields is not None else _unfunded_fields(student)
    b_fields = set(bursary["fields_of_study"])

    # Field match quality
    overlap = u_fields & b_fields
    if overlap:
        score += 30
        matched.append(f"Field of study match: {', '.join(sorted(overlap))}")

    # GPA headroom — more headroom above minimum = higher score
    min_gpa = bursary.get("min_gpa", 0.0)
    gpa_headroom = gpa - min_gpa
    if gpa_headroom >= 15:
        score += 20
        matched.append(f"GPA {gpa}% — well above minimum {min_gpa}%")
    elif gpa_headroom >= 5:
        score += 12
        matched.append(f"GPA {gpa}% meets minimum {min_gpa}%")
    else:
        score += 5
        matched.append(f"GPA {gpa}% marginally meets minimum {min_gpa}%")

    # Financial need matched
    if bursary.get("financial_need_required", False):
        score += 15
        matched.append("Financial need requirement met")

    # Nationality confirmed
    nationality = student["personal_info"].get("nationality", "")
    if nationality in bursary.get("nationality", ["South African"]):
        score += 10
        matched.append("Nationality eligible")

    # Upcoming deadline
    deadline = bursary.get("deadline", "")
    if deadline and deadline >= "2026-09-21":
        score += 5
        matched.append("Application deadline upcoming — apply soon")

    return score, matched


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_bursaries(student: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return a ranked list of bursaries the student is ELIGIBLE for.

    Scope rules:
    - Unfunded students      : all registered qualifications are in scope.
    - Multi-qual students    : only the unfunded qualification(s) are in scope.
    - Defunded students      : all registered qualifications are in scope.
    - Funded + outstanding   : all registered qualifications are in scope
                               (student may need supplementary merit funding).
    - Fully funded, no issues: no bursary recommendations returned.

    Every returned bursary passes ALL hard eligibility filters.
    """
    fs = student["funding_status"]
    u_fields = _unfunded_fields(student)

    is_nsfas_funded  = fs.get("nsfas_funded", False)
    is_defunded      = fs.get("defunded", False)
    has_outstanding  = fs.get("outstanding_balance", 0) > 0
    has_unfunded_quals = bool(fs.get("unfunded_qualifications") or u_fields)

    # Fully funded, no issues → no recommendations needed
    if (
        is_nsfas_funded
        and not is_defunded
        and not has_outstanding
        and not has_unfunded_quals
    ):
        return []

    # When funded but has outstanding fees or defunded, use all fields
    if not u_fields:
        u_fields = _get_all_student_fields(student)

    # Resolve NQF levels for the same scope
    u_nqf = _unfunded_nqf_levels(student)
    if not u_nqf:
        from data import QUALIFICATIONS_CATALOGUE
        for qual in student["academic_record"].get("registered_qualifications", []):
            cat = QUALIFICATIONS_CATALOGUE.get(qual["qualification_code"])
            if cat:
                u_nqf.add(cat["nqf_level"])

    recommendations: list[tuple[int, dict[str, Any], list[str]]] = []

    for bursary in BURSARY_CATALOGUE:
        passes, _failures = _passes_hard_filters(bursary, student, scope_fields=u_fields, scope_nqf=u_nqf)
        if not passes:
            continue  # student does not qualify — skip

        score, matched = _score_bursary(bursary, student, scope_fields=u_fields)
        recommendations.append((score, bursary, matched))

    recommendations.sort(key=lambda x: x[0], reverse=True)

    return [
        {**b, "_score": score, "_matched_criteria": matched}
        for score, b, matched in recommendations
    ]
