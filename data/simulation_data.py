"""
Simulation dataset — UNISA AI Financial Aid Assistant.

Student login uses STUDENT NUMBER (student_id) as the username.

Four scenarios:
  1. Student NOT funded by NSFAS           — 53012345  (Thabo Mokoena,   GPA 58.4%)
  2. Funded by NSFAS, outstanding fees     — 48023456  (Lerato Dlamini,  GPA 71.2%)
  3. Registered for 2 qualifications       — 51034567  (Naledi Sithole,  GPA 64.8%)
  4. Defunded by NSFAS                     — 46045678  (Sipho Nkosi,     GPA 43.1%)

All bursary links and contact details verified September 2026.
"""

from typing import Any

# ---------------------------------------------------------------------------
# Qualifications catalogue
# ---------------------------------------------------------------------------

QUALIFICATIONS_CATALOGUE: dict[str, dict[str, Any]] = {
    "BCOM001": {
        "code": "BCOM001",
        "name": "Bachelor of Commerce",
        "field_of_study": "Commerce",
        "nqf_level": 7,
        "duration_years": 3,
        "faculty": "Economic and Management Sciences",
    },
    "BSCIT002": {
        "code": "BSCIT002",
        "name": "Bachelor of Science in Information Technology",
        "field_of_study": "Information Technology",
        "nqf_level": 7,
        "duration_years": 3,
        "faculty": "Science, Engineering and Technology",
    },
    "BAPOLS003": {
        "code": "BAPOLS003",
        "name": "Bachelor of Arts in Political Science",
        "field_of_study": "Humanities",
        "nqf_level": 7,
        "duration_years": 3,
        "faculty": "Human Sciences",
    },
    "DIPBA004": {
        "code": "DIPBA004",
        "name": "Diploma in Business Administration",
        "field_of_study": "Business Administration",
        "nqf_level": 6,
        "duration_years": 3,
        "faculty": "Economic and Management Sciences",
    },
    "LLBLAW005": {
        "code": "LLBLAW005",
        "name": "Bachelor of Laws (LLB)",
        "field_of_study": "Law",
        "nqf_level": 8,
        "duration_years": 4,
        "faculty": "Law",
    },
}

# ---------------------------------------------------------------------------
# Scenario 1 — NOT funded by NSFAS  (login: 53012345)
# ---------------------------------------------------------------------------

STUDENT_NOT_FUNDED: dict[str, Any] = {
    "student_id": "53012345",
    "username": "53012345",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # Pass@1234
    "personal_info": {
        "first_name": "Thabo",
        "last_name": "Mokoena",
        "id_number": "0001015001085",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "email": "thabo.mokoena@mylife.unisa.ac.za",
        "phone": "072 123 4567",
        "home_language": "Sesotho",
        "nationality": "South African",
        "province": "Gauteng",
    },
    "financial_profile": {
        "household_income": 180_000,
        "financial_need": "Low",
    },
    "academic_record": {
        "year_of_study": 2,
        "academic_standing": "Good Standing",
        "gpa": 58.4,
        "registered_qualifications": [
            {
                "qualification_code": "BCOM001",
                "qualification_name": "Bachelor of Commerce",
                "year_enrolled": 2024,
                "status": "Active",
                "modules_registered": [
                    {"code": "ECS1601", "name": "Economics 1A", "credits": 12, "result": 62},
                    {"code": "FAC1502", "name": "Financial Accounting 1B", "credits": 12, "result": 55},
                    {"code": "MNB1501", "name": "Management of Business 1A", "credits": 12, "result": 58},
                ],
            }
        ],
    },
    "funding_status": {
        "nsfas_funded": False,
        "nsfas_application_status": "Not Applied",
        "nsfas_reference_number": None,
        "defunded": False,
        "defund_reason": None,
        "outstanding_balance": 0.00,
        "payment_history": [],
    },
    "scenario": "not_funded",
}

# ---------------------------------------------------------------------------
# Scenario 2 — Funded WITH outstanding fees  (login: 48023456)
# ---------------------------------------------------------------------------

STUDENT_FUNDED_WITH_OUTSTANDING: dict[str, Any] = {
    "student_id": "48023456",
    "username": "48023456",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # Pass@1234
    "personal_info": {
        "first_name": "Lerato",
        "last_name": "Dlamini",
        "id_number": "9812035001082",
        "date_of_birth": "1998-12-03",
        "gender": "Female",
        "email": "lerato.dlamini@mylife.unisa.ac.za",
        "phone": "083 234 5678",
        "home_language": "isiZulu",
        "nationality": "South African",
        "province": "KwaZulu-Natal",
    },
    "financial_profile": {
        "household_income": 65_000,
        "financial_need": "High",
    },
    "academic_record": {
        "year_of_study": 3,
        "academic_standing": "Good Standing",
        "gpa": 71.2,
        "registered_qualifications": [
            {
                "qualification_code": "BSCIT002",
                "qualification_name": "Bachelor of Science in Information Technology",
                "year_enrolled": 2023,
                "status": "Active",
                "modules_registered": [
                    {"code": "COS2601", "name": "Computability and Formal Languages", "credits": 12, "result": 74},
                    {"code": "COS2611", "name": "Linear Algebra", "credits": 12, "result": 69},
                    {"code": "INF2611", "name": "Information Systems 2B", "credits": 12, "result": 71},
                ],
            }
        ],
    },
    "funding_status": {
        "nsfas_funded": True,
        "nsfas_application_status": "Approved",
        "nsfas_reference_number": "NSFAS-2023-00234567",
        "defunded": False,
        "defund_reason": None,
        "outstanding_balance": 3_450.00,
        "payment_history": [
            {"date": "2026-02-15", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — Semester 1"},
            {"date": "2026-07-10", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — Semester 2"},
            {"date": "2026-09-01", "amount": 3_450.00, "status": "Pending",
             "description": "NSFAS Supplementary Module Allowance — Q3"},
        ],
        "potential_outstanding_reasons": [
            "A pending NSFAS disbursement for supplementary modules is being processed.",
            "An administrative delay in the reconciliation of module registration changes may be contributing.",
        ],
    },
    "scenario": "funded_with_outstanding",
}

# ---------------------------------------------------------------------------
# Scenario 3 — More than one qualification  (login: 51034567)
# ---------------------------------------------------------------------------

STUDENT_MULTI_QUALIFICATION: dict[str, Any] = {
    "student_id": "51034567",
    "username": "51034567",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # Pass@1234
    "personal_info": {
        "first_name": "Naledi",
        "last_name": "Sithole",
        "id_number": "0105070001083",
        "date_of_birth": "2001-05-07",
        "gender": "Female",
        "email": "naledi.sithole@mylife.unisa.ac.za",
        "phone": "076 345 6789",
        "home_language": "Setswana",
        "nationality": "South African",
        "province": "North West",
    },
    "financial_profile": {
        "household_income": 72_000,
        "financial_need": "High",
    },
    "academic_record": {
        "year_of_study": 2,
        "academic_standing": "Good Standing",
        "gpa": 64.8,
        "registered_qualifications": [
            {
                "qualification_code": "BAPOLS003",
                "qualification_name": "Bachelor of Arts in Political Science",
                "year_enrolled": 2024,
                "status": "Active",
                "nsfas_funded": True,
                "funding_note": "Primary qualification — NSFAS funding approved.",
                "modules_registered": [
                    {"code": "PLS1502", "name": "Introduction to Political Science 1B", "credits": 12, "result": 66},
                    {"code": "SOC1501", "name": "Introductory Sociology", "credits": 12, "result": 70},
                    {"code": "AFR1503", "name": "African Politics 1", "credits": 12, "result": 58},
                ],
            },
            {
                "qualification_code": "DIPBA004",
                "qualification_name": "Diploma in Business Administration",
                "year_enrolled": 2025,
                "status": "Active",
                "nsfas_funded": False,
                "funding_note": (
                    "NSFAS only funds one qualification per student at a time. "
                    "This qualification is not covered by the current NSFAS award."
                ),
                "modules_registered": [
                    {"code": "MNG2601", "name": "Management Principles 2", "credits": 12, "result": 61},
                    {"code": "BUS1501", "name": "Business Management 1A", "credits": 12, "result": 65},
                ],
            },
        ],
    },
    "funding_status": {
        "nsfas_funded": True,
        "nsfas_application_status": "Approved",
        "nsfas_reference_number": "NSFAS-2024-00345678",
        "defunded": False,
        "defund_reason": None,
        "outstanding_balance": 0.00,
        "funded_qualification": "BAPOLS003",
        "unfunded_qualifications": ["DIPBA004"],
        "payment_history": [
            {"date": "2026-02-20", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — BA Political Science Sem 1"},
            {"date": "2026-07-18", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — BA Political Science Sem 2"},
        ],
    },
    "scenario": "multi_qualification",
}

# ---------------------------------------------------------------------------
# Scenario 4 — DEFUNDED  (login: 46045678)
# ---------------------------------------------------------------------------

STUDENT_DEFUNDED: dict[str, Any] = {
    "student_id": "46045678",
    "username": "46045678",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # Pass@1234
    "personal_info": {
        "first_name": "Sipho",
        "last_name": "Nkosi",
        "id_number": "9803085001081",
        "date_of_birth": "1998-03-08",
        "gender": "Male",
        "email": "sipho.nkosi@mylife.unisa.ac.za",
        "phone": "071 456 7890",
        "home_language": "isiXhosa",
        "nationality": "South African",
        "province": "Eastern Cape",
    },
    "financial_profile": {
        "household_income": 58_000,
        "financial_need": "High",
    },
    "academic_record": {
        "year_of_study": 4,
        "academic_standing": "Academic Risk",
        "gpa": 43.1,
        "registered_qualifications": [
            {
                "qualification_code": "LLBLAW005",
                "qualification_name": "Bachelor of Laws (LLB)",
                "year_enrolled": 2022,
                "status": "Active",
                "modules_registered": [
                    {"code": "PVL3702", "name": "Law of Persons and Family", "credits": 12, "result": 44},
                    {"code": "CRW2601", "name": "Criminal Law", "credits": 12, "result": 41},
                    {"code": "MRL3702", "name": "Mercantile Law 3B", "credits": 12, "result": None},
                ],
            }
        ],
    },
    "funding_status": {
        "nsfas_funded": False,
        "nsfas_application_status": "Defunded",
        "nsfas_reference_number": "NSFAS-2022-00456789",
        "defunded": True,
        "defund_reason": (
            "Student did not meet the minimum academic progression requirements "
            "as stipulated in the NSFAS Bursary Agreement (N+2 rule). "
            "Cumulative pass rate fell below the 50% threshold in the 2025 academic year."
        ),
        "defund_date": "2026-01-15",
        "outstanding_balance": 8_900.00,
        "appeal_deadline": "2026-10-31",
        "payment_history": [
            {"date": "2022-02-10", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 1 Sem 1"},
            {"date": "2022-07-15", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 1 Sem 2"},
            {"date": "2023-02-12", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 2 Sem 1"},
            {"date": "2023-07-14", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 2 Sem 2"},
            {"date": "2024-02-10", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 3 Sem 1"},
            {"date": "2024-07-11", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 3 Sem 2"},
            {"date": "2025-02-08", "amount": 15_000.00, "status": "Paid",
             "description": "NSFAS Tuition Disbursement — LLB Year 4 Sem 1"},
            {"date": "2025-07-09", "amount": 0.00, "status": "Cancelled",
             "description": "NSFAS Disbursement — LLB Year 4 Sem 2 (Defunding in progress)"},
            {"date": "2026-01-15", "amount": 8_900.00, "status": "Outstanding",
             "description": "Remaining tuition balance after NSFAS defunding — student liable"},
        ],
    },
    "scenario": "defunded",
}

# ---------------------------------------------------------------------------
# Master registries
# ---------------------------------------------------------------------------

STUDENT_DATABASE: dict[str, dict[str, Any]] = {
    STUDENT_NOT_FUNDED["username"]:              STUDENT_NOT_FUNDED,
    STUDENT_FUNDED_WITH_OUTSTANDING["username"]: STUDENT_FUNDED_WITH_OUTSTANDING,
    STUDENT_MULTI_QUALIFICATION["username"]:     STUDENT_MULTI_QUALIFICATION,
    STUDENT_DEFUNDED["username"]:                STUDENT_DEFUNDED,
}

STUDENT_DATABASE_BY_ID: dict[str, dict[str, Any]] = {
    v["student_id"]: v for v in STUDENT_DATABASE.values()
}

# ---------------------------------------------------------------------------
# Bursary catalogue — all entries verified September 2026.
#
# Eligibility fields used by the hard-filter matching engine:
#   fields_of_study        – list of field labels (hard filter — must overlap)
#   nqf_levels             – list of NQF levels (hard filter)
#   min_gpa                – minimum GPA % (hard filter — student must meet or exceed)
#   financial_need_required– if True, household income must be ≤ income_ceiling
#   income_ceiling         – explicit ZAR ceiling (defaults to R350 000 when None)
#   nationality            – list of eligible nationalities
#   min_year_of_study      – minimum year of study (hard filter)
#   qualification_type     – "undergraduate" | "postgraduate" | "both"
# ---------------------------------------------------------------------------

BURSARY_CATALOGUE: list[dict[str, Any]] = [

    # ── Commerce (GPA ≥ 60%) ──────────────────────────────────────────────
    {
        "id": "B001",
        "name": "Standard Bank Group Bursary",
        "funder": "Standard Bank Group",
        "fields_of_study": ["Commerce", "Finance", "Accounting", "Information Technology"],
        "nqf_levels": [7, 8],
        "qualification_type": "undergraduate",
        "min_gpa": 60.0,
        "financial_need_required": False,
        "income_ceiling": None,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 60_000,
        # Verified: standardbank.com official bursary page (Sep 2026)
        "application_url": "https://www.standardbank.com/sbg/standard-bank-group/careers/early-careers/bursaries",
        "deadline": "2026-11-30",
        "description": (
            "Covers tuition and provides a living allowance for students in Commerce, Finance, "
            "Accounting and IT. Applications are administered by StudyTrust on behalf of "
            "Standard Bank Group."
        ),
    },

    # ── Accounting CA-track (GPA ≥ 65%) ──────────────────────────────────
    {
        "id": "B002",
        "name": "PwC CA Bursary Programme",
        "funder": "PricewaterhouseCoopers South Africa",
        "fields_of_study": ["Accounting", "Commerce"],
        "nqf_levels": [7],
        "qualification_type": "undergraduate",
        "min_gpa": 65.0,
        "financial_need_required": False,
        "income_ceiling": None,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 65_000,
        # Verified: pwc.co.za learners bursaries page (Sep 2026)
        "application_url": "https://www.pwc.co.za/en/careers/learners/learners-bursaries.html",
        "deadline": "2026-10-31",
        "description": (
            "PwC supports 500+ students annually through its CA bursary. "
            "Covers tuition and study materials and includes vacation work opportunities. "
            "Open to aspiring Chartered Accountants at SAICA-accredited universities."
        ),
    },

    # ── Accounting — financially needy (GPA ≥ 55%) ───────────────────────
    {
        "id": "B003",
        "name": "SAICA Thuthuka Bursary Fund",
        "funder": "South African Institute of Chartered Accountants (SAICA)",
        "fields_of_study": ["Accounting", "Commerce"],
        "nqf_levels": [7],
        "qualification_type": "undergraduate",
        "min_gpa": 55.0,
        "financial_need_required": True,
        "income_ceiling": 350_000,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 70_000,
        # Verified: saica.org.za Thuthuka page (Sep 2026)
        "application_url": "https://www.saica.org.za/thuthuka-education-upliftment-fund",
        "deadline": "2026-10-15",
        "description": (
            "Full bursary for Black African and Coloured students studying towards "
            "becoming a Chartered Accountant (CA(SA)) at a SAICA-accredited university. "
            "Covers tuition, accommodation, study materials and a monthly allowance."
        ),
    },

    # ── Commerce — financially needy, lower GPA (GPA ≥ 50%) ─────────────
    {
        "id": "B004",
        "name": "National Treasury Bursary Scheme",
        "funder": "National Treasury (South Africa)",
        "fields_of_study": ["Commerce", "Finance", "Accounting", "Business Administration"],
        "nqf_levels": [6, 7, 8],
        "qualification_type": "undergraduate",
        "min_gpa": 50.0,
        "financial_need_required": True,
        "income_ceiling": 350_000,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 50_000,
        # Verified: treasury.gov.za graduate bursary page (Sep 2026)
        "application_url": "https://www.treasury.gov.za/graduate/",
        "deadline": "2026-09-30",
        "description": (
            "Government bursary for financially needy students in Commerce, Finance, "
            "Accounting and Business Administration. Covers tuition, accommodation "
            "and prescribed textbooks. Apply to bursaries@treasury.gov.za."
        ),
    },

    # ── IT (GPA ≥ 65%) ────────────────────────────────────────────────────
    {
        "id": "B005",
        "name": "Sasol Bursary Programme",
        "funder": "Sasol",
        "fields_of_study": ["Engineering", "Information Technology", "Science"],
        "nqf_levels": [7, 8],
        "qualification_type": "undergraduate",
        "min_gpa": 65.0,
        "financial_need_required": False,
        "income_ceiling": None,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 80_000,
        # Verified: sasol.com/careers/careers/students (Sep 2026)
        "application_url": "https://www.sasol.com/careers/careers/students",
        "deadline": "2026-11-30",
        "description": (
            "Talent-based bursary covering 100% of tuition, registration, exam fees, "
            "accommodation, meals, book allowance and a merit bonus. "
            "Includes vacation work with a paid salary from second year."
        ),
    },

    # ── IT — lower GPA (GPA ≥ 60%) ───────────────────────────────────────
    {
        "id": "B006",
        "name": "Standard Bank IT Bursary",
        "funder": "Standard Bank Group",
        "fields_of_study": ["Information Technology"],
        "nqf_levels": [7],
        "qualification_type": "undergraduate",
        "min_gpa": 60.0,
        "financial_need_required": False,
        "income_ceiling": None,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 60_000,
        # Verified: standardbank.com official bursary page (Sep 2026)
        "application_url": "https://www.standardbank.com/sbg/standard-bank-group/careers/early-careers/bursaries",
        "deadline": "2026-11-30",
        "description": (
            "Standard Bank bursary specifically for Information Technology students. "
            "Covers full tuition plus a monthly living allowance. "
            "Administered by StudyTrust on behalf of Standard Bank Group."
        ),
    },

    # ── Humanities / Political Science (GPA ≥ 55%) ───────────────────────
    {
        "id": "B007",
        "name": "Department of Social Development Bursary",
        "funder": "Department of Social Development (SA Government)",
        "fields_of_study": ["Humanities", "Social Work", "Psychology"],
        "nqf_levels": [7, 8],
        "qualification_type": "undergraduate",
        "min_gpa": 55.0,
        "financial_need_required": True,
        "income_ceiling": 350_000,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 35_000,
        # Verified: dsd.gov.za bursaries page (Sep 2026)
        "application_url": "https://www.dsd.gov.za/index.php/bursaries",
        "deadline": "2026-11-30",
        "description": (
            "Government bursary for financially needy students in social development, "
            "social work, psychology and related humanities disciplines."
        ),
    },

    # ── Business Administration (GPA ≥ 55%) ──────────────────────────────
    {
        "id": "B008",
        "name": "National Treasury — Business Admin Bursary",
        "funder": "National Treasury (South Africa)",
        "fields_of_study": ["Business Administration"],
        "nqf_levels": [6, 7],
        "qualification_type": "undergraduate",
        "min_gpa": 55.0,
        "financial_need_required": True,
        "income_ceiling": 350_000,
        "nationality": ["South African"],
        "min_year_of_study": 1,
        "amount": 50_000,
        # Verified: treasury.gov.za graduate bursary page (Sep 2026)
        "application_url": "https://www.treasury.gov.za/graduate/",
        "deadline": "2026-09-30",
        "description": (
            "Government bursary for financially needy students in Business Administration "
            "at NQF Level 6 or 7. Covers tuition, accommodation and prescribed textbooks."
        ),
    },

    # ── Law (GPA ≥ 40%, year 4) ───────────────────────────────────────────
    {
        "id": "B009",
        "name": "Legal Practitioners Fidelity Fund Bursary",
        "funder": "Legal Practitioners Fidelity Fund",
        "fields_of_study": ["Law"],
        "nqf_levels": [8],
        "qualification_type": "undergraduate",
        "min_gpa": 40.0,
        "financial_need_required": True,
        "income_ceiling": 350_000,
        "nationality": ["South African"],
        "min_year_of_study": 3,
        "amount": 40_000,
        # Verified: lssa.org.za (Sep 2026)
        "application_url": "https://www.lssa.org.za/",
        "deadline": "2026-08-15",
        "description": (
            "Bursary for LLB students who have completed at least the first two years "
            "of the 4-year LLB curriculum. Intended for students in serious financial need. "
            "Covers tuition fees for up to 2 years."
        ),
    },

    # ── All fields — high merit (GPA ≥ 75%) ──────────────────────────────
    {
        "id": "B010",
        "name": "UNISA Prestige Scholarship",
        "funder": "University of South Africa (UNISA)",
        "fields_of_study": [
            "Commerce", "Information Technology", "Science", "Humanities",
            "Law", "Business Administration", "Accounting", "Finance",
        ],
        "nqf_levels": [6, 7, 8],
        "qualification_type": "undergraduate",
        "min_gpa": 75.0,
        "financial_need_required": False,
        "income_ceiling": None,
        "nationality": ["South African", "Other"],
        "min_year_of_study": 1,
        "amount": 30_000,
        # Verified: unisa.ac.za scholarships page (Sep 2026)
        "application_url": "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding/Scholarships",
        "deadline": "2026-10-30",
        "description": (
            "Merit-based scholarship for top-performing UNISA students across all faculties. "
            "Covers partial tuition. Requires a minimum 75% average. "
            "No financial need criterion."
        ),
    },
]

# ---------------------------------------------------------------------------
# Alternative financial aid partners — verified September 2026
# ---------------------------------------------------------------------------

ALTERNATIVE_FUNDING_PARTNERS: list[dict[str, Any]] = [
    {
        "id": "AF001",
        "name": "Ikusasa Student Financial Aid Programme (ISFAP)",
        "type": "Hybrid Bursary / Loan",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_min": 0,
        "income_threshold": 600_000,
        "nsfas_eligible": False,
        "description": (
            "Provides financial support to 'missing middle' students who do not qualify for NSFAS "
            "but cannot afford university fees. Covers tuition, accommodation and living expenses."
        ),
        "eligibility": [
            "South African citizen",
            "Household income between R0 and R600 000 per annum",
            "Enrolled at a participating public university",
            "Not in receipt of a full NSFAS bursary",
        ],
        # Verified: pg.isfap.org.za online application portal (Sep 2026)
        "application_url": "https://pg.isfap.org.za/",
        "deadline": "2026-11-30",
        "contact_email": "info@isfap.org.za",
    },
    {
        "id": "AF002",
        "name": "UNISA Student Financial Aid Fund (SFAF)",
        "type": "Emergency Bursary",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_min": 0,
        "income_threshold": 350_000,
        "nsfas_eligible": None,
        "description": (
            "UNISA's internal emergency financial aid fund for registered students facing acute "
            "financial hardship and at risk of deregistration due to outstanding fees."
        ),
        "eligibility": [
            "Currently registered UNISA student",
            "Demonstrable financial hardship",
            "Not in receipt of a full bursary that covers all fees",
        ],
        # Verified: unisa.ac.za fees & funding page (Sep 2026)
        "application_url": "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding",
        "deadline": "Rolling — apply as early as possible",
        "contact_email": "finan@unisa.ac.za",
    },
    {
        "id": "AF003",
        "name": "Fundi Student Loan",
        "type": "Student Loan",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_min": 0,
        "income_threshold": None,
        "nsfas_eligible": None,
        "description": (
            "Private student loan covering tuition, registration, accommodation and study materials. "
            "Fundi Capital (Pty) Ltd is a registered credit provider (NCRCP 158). "
            "Repayment commences after graduation."
        ),
        "eligibility": [
            "South African citizen or permanent resident",
            "Enrolled at an accredited institution",
            "Guarantor required if the student has no income",
        ],
        # Verified: fundifinance.co.za active (Sep 2026)
        "application_url": "https://fundifinance.co.za/",
        "deadline": "Rolling — apply anytime",
        "contact_email": "info@fundifinance.co.za",
    },
]
