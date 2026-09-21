"""
Simulation dataset for the AI-Powered Student Funding & Financial Assistance System.

Covers four scenarios:
  1. Student NOT funded by NSFAS
  2. Student funded by NSFAS WITH outstanding fees
  3. Student registered for MORE THAN ONE qualification
  4. Student who has been DEFUNDED by NSFAS
"""

from typing import Any

# ---------------------------------------------------------------------------
# Shared lookup tables
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
# Scenario 1 — Student NOT funded by NSFAS
# ---------------------------------------------------------------------------

STUDENT_NOT_FUNDED: dict[str, Any] = {
    "student_id": "53012345",
    "username": "thabo.mokoena",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # "Pass@1234"
    "personal_info": {
        "first_name": "Thabo",
        "last_name": "Mokoena",
        "id_number": "0001015001085",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "email": "thabo.mokoena@mylife.unisa.ac.za",
        "phone": "0721234567",
        "home_language": "Sesotho",
        "nationality": "South African",
        "province": "Gauteng",
    },
    "financial_profile": {
        "household_income": 180_000,          # annual, ZAR — above NSFAS cap
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
# Scenario 2 — Student funded by NSFAS WITH outstanding fees
# ---------------------------------------------------------------------------

STUDENT_FUNDED_WITH_OUTSTANDING: dict[str, Any] = {
    "student_id": "48023456",
    "username": "lerato.dlamini",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # "Pass@1234"
    "personal_info": {
        "first_name": "Lerato",
        "last_name": "Dlamini",
        "id_number": "9812035001082",
        "date_of_birth": "1998-12-03",
        "gender": "Female",
        "email": "lerato.dlamini@mylife.unisa.ac.za",
        "phone": "0832345678",
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
        "outstanding_balance": 3_450.00,  # ZAR — partial payment pending
        "payment_history": [
            {
                "date": "2026-02-15",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — Semester 1",
            },
            {
                "date": "2026-07-10",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — Semester 2",
            },
            {
                "date": "2026-09-01",
                "amount": 3_450.00,
                "status": "Pending",
                "description": "NSFAS Supplementary Module Allowance — Q3",
            },
        ],
        "potential_outstanding_reasons": [
            "Pending NSFAS disbursement for supplementary modules — payment is being processed.",
            "Administrative delay in the reconciliation of module registration changes.",
        ],
    },
    "scenario": "funded_with_outstanding",
}

# ---------------------------------------------------------------------------
# Scenario 3 — Student registered for MORE THAN ONE qualification
# ---------------------------------------------------------------------------

STUDENT_MULTI_QUALIFICATION: dict[str, Any] = {
    "student_id": "51034567",
    "username": "naledi.sithole",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # "Pass@1234"
    "personal_info": {
        "first_name": "Naledi",
        "last_name": "Sithole",
        "id_number": "0105070001083",
        "date_of_birth": "2001-05-07",
        "gender": "Female",
        "email": "naledi.sithole@mylife.unisa.ac.za",
        "phone": "0763456789",
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
            {
                "date": "2026-02-20",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — BA Political Science Sem 1",
            },
            {
                "date": "2026-07-18",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — BA Political Science Sem 2",
            },
        ],
    },
    "scenario": "multi_qualification",
}

# ---------------------------------------------------------------------------
# Scenario 4 — Student who has been DEFUNDED
# ---------------------------------------------------------------------------

STUDENT_DEFUNDED: dict[str, Any] = {
    "student_id": "46045678",
    "username": "sipho.nkosi",
    "password_hash": "$2b$12$3xhM3xsEt1/7wxYquGs0O.PNTeY9ZZzLwlMB8l4qG/k0cYdCmedES",  # "Pass@1234"
    "personal_info": {
        "first_name": "Sipho",
        "last_name": "Nkosi",
        "id_number": "9803085001081",
        "date_of_birth": "1998-03-08",
        "gender": "Male",
        "email": "sipho.nkosi@mylife.unisa.ac.za",
        "phone": "0714567890",
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
                    {"code": "MRL3702", "name": "Mercantile Law 3B", "credits": 12, "result": None},  # incomplete
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
        "payment_history": [
            {
                "date": "2022-02-10",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 1 Sem 1",
            },
            {
                "date": "2022-07-15",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 1 Sem 2",
            },
            {
                "date": "2023-02-12",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 2 Sem 1",
            },
            {
                "date": "2023-07-14",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 2 Sem 2",
            },
            {
                "date": "2024-02-10",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 3 Sem 1",
            },
            {
                "date": "2024-07-11",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 3 Sem 2",
            },
            {
                "date": "2025-02-08",
                "amount": 15_000.00,
                "status": "Paid",
                "description": "NSFAS Tuition Disbursement — LLB Year 4 Sem 1",
            },
            {
                "date": "2025-07-09",
                "amount": 0.00,
                "status": "Cancelled",
                "description": "NSFAS Disbursement — LLB Year 4 Sem 2 (Defunding in progress)",
            },
            {
                "date": "2026-01-15",
                "amount": 8_900.00,
                "status": "Outstanding",
                "description": "Remaining tuition balance after NSFAS defunding — student liable",
            },
        ],
        "appeal_deadline": "2026-10-31",
    },
    "scenario": "defunded",
}

# ---------------------------------------------------------------------------
# Master registry — keyed by username for easy lookup
# ---------------------------------------------------------------------------

STUDENT_DATABASE: dict[str, dict[str, Any]] = {
    STUDENT_NOT_FUNDED["username"]: STUDENT_NOT_FUNDED,
    STUDENT_FUNDED_WITH_OUTSTANDING["username"]: STUDENT_FUNDED_WITH_OUTSTANDING,
    STUDENT_MULTI_QUALIFICATION["username"]: STUDENT_MULTI_QUALIFICATION,
    STUDENT_DEFUNDED["username"]: STUDENT_DEFUNDED,
}

# Convenience: lookup by student_id as well
STUDENT_DATABASE_BY_ID: dict[str, dict[str, Any]] = {
    v["student_id"]: v for v in STUDENT_DATABASE.values()
}

# ---------------------------------------------------------------------------
# Bursary catalogue (used by recommendation engine)
# ---------------------------------------------------------------------------

BURSARY_CATALOGUE: list[dict[str, Any]] = [
    {
        "id": "B001",
        "name": "Sasol Bursary Programme",
        "funder": "Sasol",
        "fields_of_study": ["Engineering", "Information Technology", "Science"],
        "nqf_levels": [7, 8],
        "min_gpa": 65.0,
        "financial_need_required": True,
        "nationality": ["South African"],
        "amount": 80_000,
        "application_url": "https://www.sasol.com/careers/bursaries",
        "deadline": "2026-11-30",
        "description": "Full bursary covering tuition, accommodation and a monthly stipend for STEM students.",
    },
    {
        "id": "B002",
        "name": "Standard Bank Bursary",
        "funder": "Standard Bank",
        "fields_of_study": ["Commerce", "Finance", "Accounting", "Information Technology"],
        "nqf_levels": [7, 8],
        "min_gpa": 60.0,
        "financial_need_required": False,
        "nationality": ["South African"],
        "amount": 60_000,
        "application_url": "https://www.standardbank.co.za/pages/careers/bursaries",
        "deadline": "2026-10-15",
        "description": "Covers tuition and offers a living allowance for high-achieving Commerce and IT students.",
    },
    {
        "id": "B003",
        "name": "National Research Foundation (NRF) Scholarship",
        "funder": "NRF",
        "fields_of_study": ["Science", "Engineering", "Information Technology", "Humanities"],
        "nqf_levels": [7, 8, 9],
        "min_gpa": 70.0,
        "financial_need_required": False,
        "nationality": ["South African"],
        "amount": 50_000,
        "application_url": "https://www.nrf.ac.za/funding/",
        "deadline": "2026-12-01",
        "description": "Merit-based scholarship supporting undergraduate and postgraduate research-track students.",
    },
    {
        "id": "B004",
        "name": "FirstRand Empowerment Foundation Bursary",
        "funder": "FirstRand",
        "fields_of_study": ["Commerce", "Business Administration", "Finance", "Law"],
        "nqf_levels": [6, 7, 8],
        "min_gpa": 55.0,
        "financial_need_required": True,
        "nationality": ["South African"],
        "amount": 45_000,
        "application_url": "https://www.firstrand.co.za/sustainability/empowerment-foundation/",
        "deadline": "2026-11-01",
        "description": "Supports financially needy students pursuing Commerce, Law, and Business qualifications.",
    },
    {
        "id": "B005",
        "name": "Thuthuka Bursary Fund (SAICA)",
        "funder": "SAICA",
        "fields_of_study": ["Accounting", "Commerce"],
        "nqf_levels": [7],
        "min_gpa": 60.0,
        "financial_need_required": True,
        "nationality": ["South African"],
        "amount": 70_000,
        "application_url": "https://www.saica.co.za/thuthuka",
        "deadline": "2026-09-30",
        "description": "Dedicated to developing Black African and Coloured CA(SA) candidates. Covers full tuition and accommodation.",
    },
    {
        "id": "B006",
        "name": "Law Society of South Africa Bursary",
        "funder": "Law Society of South Africa",
        "fields_of_study": ["Law"],
        "nqf_levels": [8],
        "min_gpa": 55.0,
        "financial_need_required": True,
        "nationality": ["South African"],
        "amount": 40_000,
        "application_url": "https://www.lssa.org.za/",
        "deadline": "2026-11-15",
        "description": "Supports financially needy LLB students committed to a career in the legal profession.",
    },
    {
        "id": "B007",
        "name": "Eskom STEM Bursary",
        "funder": "Eskom",
        "fields_of_study": ["Engineering", "Information Technology", "Science"],
        "nqf_levels": [7, 8],
        "min_gpa": 65.0,
        "financial_need_required": False,
        "nationality": ["South African"],
        "amount": 75_000,
        "application_url": "https://www.eskom.co.za/careers/bursaries/",
        "deadline": "2026-10-31",
        "description": "Full tuition plus living allowance for engineering and IT students committed to South Africa's energy sector.",
    },
    {
        "id": "B008",
        "name": "PwC Bursary Programme",
        "funder": "PricewaterhouseCoopers",
        "fields_of_study": ["Accounting", "Commerce", "Finance"],
        "nqf_levels": [7],
        "min_gpa": 65.0,
        "financial_need_required": False,
        "nationality": ["South African"],
        "amount": 65_000,
        "application_url": "https://www.pwc.co.za/en/careers/student-careers/bursaries.html",
        "deadline": "2026-10-01",
        "description": "Merit-based bursary for aspiring chartered accountants and finance professionals.",
    },
    {
        "id": "B009",
        "name": "UNISA Prestige Scholarship",
        "funder": "UNISA",
        "fields_of_study": [
            "Commerce", "Information Technology", "Science", "Humanities",
            "Law", "Business Administration",
        ],
        "nqf_levels": [6, 7, 8],
        "min_gpa": 75.0,
        "financial_need_required": False,
        "nationality": ["South African", "Other"],
        "amount": 30_000,
        "application_url": "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding/Scholarships",
        "deadline": "2026-10-30",
        "description": "Awarded to top-performing UNISA students across all faculties. Covers partial tuition.",
    },
    {
        "id": "B010",
        "name": "Department of Social Development Bursary",
        "funder": "Department of Social Development (SA Government)",
        "fields_of_study": ["Humanities", "Social Work", "Psychology"],
        "nqf_levels": [7, 8],
        "min_gpa": 55.0,
        "financial_need_required": True,
        "nationality": ["South African"],
        "amount": 35_000,
        "application_url": "https://www.dsd.gov.za/index.php/bursaries",
        "deadline": "2026-11-30",
        "description": "Government bursary for students in social development and humanities disciplines.",
    },
]

# ---------------------------------------------------------------------------
# UNISA alternative financial aid partners
# ---------------------------------------------------------------------------

ALTERNATIVE_FUNDING_PARTNERS: list[dict[str, Any]] = [
    {
        "id": "AF001",
        "name": "Ikusasa Student Financial Aid Programme (ISFAP)",
        "type": "Hybrid Bursary/Loan",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_threshold": 600_000,
        "description": (
            "Provides financial support to 'missing middle' students who do not qualify for NSFAS "
            "but cannot afford university fees. Covers tuition, accommodation, and living expenses."
        ),
        "eligibility": [
            "South African citizen",
            "Combined household income between R350 001 and R600 000 per annum",
            "Enrolled at a public university",
            "Not funded by NSFAS",
        ],
        "application_url": "https://isfap.co.za/",
        "deadline": "2026-11-30",
        "contact_email": "info@isfap.co.za",
    },
    {
        "id": "AF002",
        "name": "UNISA Student Financial Aid Fund (SFAF)",
        "type": "Emergency Bursary",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_threshold": 350_000,
        "description": (
            "UNISA's internal emergency financial aid fund for registered students who face acute "
            "financial hardship and are at risk of deregistration due to outstanding fees."
        ),
        "eligibility": [
            "Currently registered UNISA student",
            "Demonstrable financial hardship",
            "Not in receipt of full NSFAS or other full bursary",
        ],
        "application_url": "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding/Student-Financial-Aid-Fund",
        "deadline": "Rolling — apply as early as possible",
        "contact_email": "studentfinance@unisa.ac.za",
    },
    {
        "id": "AF003",
        "name": "Fundi Student Loan",
        "type": "Student Loan",
        "fields_of_study": ["All"],
        "nqf_levels": [6, 7, 8],
        "income_threshold": None,
        "description": (
            "A private student loan facility that covers tuition, accommodation, and study materials. "
            "Repayment commences after graduation."
        ),
        "eligibility": [
            "South African citizen or permanent resident",
            "Enrolled at an accredited institution",
            "Guarantor (parent/guardian) required for students under 18",
        ],
        "application_url": "https://www.fundi.co.za/",
        "deadline": "Rolling applications",
        "contact_email": "info@fundi.co.za",
    },
    {
        "id": "AF004",
        "name": "Old Mutual Student Bursary Loan",
        "type": "Bursary Loan",
        "fields_of_study": ["Commerce", "Finance", "Accounting", "Information Technology"],
        "nqf_levels": [7, 8],
        "income_threshold": None,
        "description": (
            "Old Mutual offers a blended bursary-loan product for qualifying students in Commerce, "
            "Finance, and IT fields. Top performers may qualify for loan-to-bursary conversion."
        ),
        "eligibility": [
            "South African citizen",
            "Minimum 60% average in the previous academic year",
            "Enrolled in a qualifying field of study",
        ],
        "application_url": "https://www.oldmutual.co.za/personal/education/student-bursary-loan/",
        "deadline": "2026-10-15",
        "contact_email": "bursaries@oldmutual.com",
    },
]
