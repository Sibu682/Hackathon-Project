"""
Application-wide configuration and constants.
All contact details verified against official sources (September 2026).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AI provider — Groq (OpenAI-compatible API)
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
AI_MODEL: str = os.getenv("AI_MODEL", "openai/gpt-oss-120b")

# NSFAS — verified from official NSFAS letterhead (nsfas.org.za, March 2026)
NSFAS_WEBSITE: str = "https://www.nsfas.org.za"
NSFAS_APPLY_URL: str = "https://my.nsfas.org.za"
NSFAS_HELPLINE: str = "0800 067 327"          # toll-free, verified from NSFAS letterhead
NSFAS_PHONE_ALT: str = "021 763 3200"          # Cape Town office
NSFAS_EMAIL: str = "info@nsfas.org.za"         # verified from NSFAS letterhead

# UNISA — verified from unisa.ac.za/Contact-us (September 2026)
# Central student enquiries toll-free line (Mon–Fri 08:00–19:00, Sat 08:00–14:00)
UNISA_CONTACT_CENTRE: str = "0800 00 1870"
UNISA_FINANCE_EMAIL: str = "finan@unisa.ac.za"   # verified from official UNISA refund form
UNISA_FINANCE_PHONE: str = "0800 00 1870"         # route through central contact centre
UNISA_FINANCE_URL: str = "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding"
UNISA_NSFAS_APPEAL_URL: str = "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding/NSFAS"
UNISA_CONTACT_URL: str = "https://www.unisa.ac.za/sites/corporate/default/Contact-us"

# Application
APP_NAME: str = "UNISA Financial Aid Assistant"
APP_VERSION: str = "1.0.0"
