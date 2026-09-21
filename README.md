# UNISA AI-Powered Student Funding & Financial Assistance System

An AI-powered CLI application that integrates with the UNISA student portal to help students understand their NSFAS funding status, manage outstanding fees, and discover alternative financial aid opportunities.

---

## Features

| Feature | Description |
|---|---|
| **Secure Login** | Student portal authentication with bcrypt password hashing and 3-attempt lockout |
| **AI Funding Detection** | OpenAI-powered agent (with deterministic fallback) analyses NSFAS status and produces personalised guidance |
| **Financial Aid Dashboard** | Full overview of funding status, registration, outstanding fees, and payment history |
| **Defunded Student Support** | Formal notice, UNISA contact details, and a step-by-step NSFAS appeal guide |
| **Multi-Qualification Analysis** | Per-qualification NSFAS funding breakdown and eligibility warnings |
| **Bursary Recommendations** | Scored, ranked bursary matches based on GPA, field of study, and financial need |
| **Alternative Funding** | UNISA-partnered and government schemes matched to the student's profile |

---

## Project Structure

```
Hackathon Project/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── smoke_test.py               # Basic integrity checks
│
├── config/
│   ├── __init__.py
│   └── settings.py             # App constants, URLs, contact details
│
├── data/
│   ├── __init__.py
│   └── simulation_data.py      # 4 student scenarios + bursary catalogue
│
└── src/
    ├── __init__.py
    ├── auth.py                 # Authentication module
    ├── ai_agent.py             # AI agent core (OpenAI + rule-based fallback)
    ├── dashboard.py            # Financial aid dashboard renderer
    ├── defunded_support.py     # Defunded student support & appeals
    ├── multi_qual_analysis.py  # Multi-qualification funding analysis
    ├── bursary_recommender.py  # Personalised bursary matching engine
    └── alternative_funding.py  # Alternative financial aid schemes
```

---

## Simulation Scenarios

All four demo students share the password **`Pass@1234`**.

| Username | Scenario | Student |
|---|---|---|
| `thabo.mokoena` | Not funded by NSFAS | Thabo Mokoena |
| `lerato.dlamini` | Funded — with outstanding fees | Lerato Dlamini |
| `naledi.sithole` | Funded — registered for 2 qualifications | Naledi Sithole |
| `sipho.nkosi` | Previously funded — defunded | Sipho Nkosi |

### Scenario Details

**Scenario 1 — Not Funded (Thabo Mokoena)**
- BCom student, household income above NSFAS threshold (R180 000/year)
- System shows NSFAS application guidance, links to apply, and matched bursaries

**Scenario 2 — Funded with Outstanding Fees (Lerato Dlamini)**
- BSc IT student, NSFAS approved, R3 450 outstanding balance
- Pending supplementary module disbursement; system shows possible reasons (not confirmed)

**Scenario 3 — Multi-Qualification (Naledi Sithole)**
- Registered for BA Political Science (NSFAS-funded) and Diploma in Business Administration (not funded)
- System explains the one-qualification-per-student NSFAS rule and recommends bursaries for the unfunded diploma

**Scenario 4 — Defunded (Sipho Nkosi)**
- LLB student, defunded in January 2026 for failing to meet the N+2 academic progression rule
- R8 900 outstanding balance; system shows formal defund notice, UNISA contacts, and a 5-step appeal guide

---

## Setup

### 1. Prerequisites

- Python 3.9 or higher
- `pip` or `pip3`

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure environment (optional — for AI mode)

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

If no API key is set the system automatically uses the built-in rule-based engine. All core functionality works without an OpenAI account.

---

## Running the Application

### Demo mode (recommended — no login required)

```bash
python3 main.py --demo
```

An interactive menu lets you pick any of the four simulation scenarios.

### Standard mode (portal login)

```bash
python3 main.py
```

Enter one of the usernames and the password `Pass@1234` when prompted.

---

## How the AI Agent Works

```
Student logs in
      │
      ▼
AI Agent analyses funding data
      │
      ├─── No NSFAS record ──────────► Apply for NSFAS view
      │                                 + Bursary recommendations
      │                                 + Alternative funding
      │
      ├─── NSFAS funded ─────────────► Financial Aid Dashboard
      │         │                       + Multi-qual analysis (if applicable)
      │         └─── Outstanding fees   + Bursary recommendations
      │                                 + Alternative funding
      │
      └─── Defunded ─────────────────► Dashboard + Defund Notice
                                        + Appeal guide + Contacts
                                        + Bursary recommendations
                                        + Alternative funding
```

The agent uses OpenAI function-calling (`gpt-4o-mini` by default) to produce a structured `assess_nsfas_status` response. When no API key is configured, a deterministic rule engine produces the same output format so the application is fully functional offline.

**Important design decision:** The agent is explicitly instructed never to assert that a student has been defunded, or that NSFAS has delayed a payment, unless the data explicitly confirms it. Potential reasons for outstanding fees are always framed as possibilities, not confirmed facts.

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai` | AI agent via OpenAI chat completions API |
| `rich` | Terminal UI — panels, tables, coloured output |
| `questionary` | Interactive scenario picker in demo mode |
| `bcrypt` | Password hashing and verification |
| `python-dotenv` | `.env` file loading |
| `pydantic` | Data validation (available for extension) |

---

## Contact Information Embedded in the System

| Contact Point | Details |
|---|---|
| NSFAS Helpline (toll-free) | 0800 067 327 |
| NSFAS Email | info@nsfas.org.za |
| NSFAS Website | https://www.nsfas.org.za |
| UNISA Student Finance Phone | 012 441 5873 |
| UNISA Student Finance Email | studentfinance@unisa.ac.za |

---

## Disclaimer

This is a hackathon prototype. Funding information, contact details, and bursary data are based on publicly available information at the time of development and may change. All bursary and alternative funding details should be verified directly with the relevant funder before applying. The AI agent's assessments are guidance only and do not constitute official NSFAS or UNISA determinations.
