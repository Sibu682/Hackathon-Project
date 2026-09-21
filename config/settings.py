"""
Application-wide configuration and constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")

# NSFAS
NSFAS_WEBSITE: str = "https://www.nsfas.org.za"
NSFAS_APPLY_URL: str = "https://my.nsfas.org.za/mynsfas/index.html"
NSFAS_HELPLINE: str = "0800 067 327"
NSFAS_EMAIL: str = "info@nsfas.org.za"

# UNISA Student Finance
UNISA_FINANCE_EMAIL: str = "studentfinance@unisa.ac.za"
UNISA_FINANCE_PHONE: str = "012 441 5873"
UNISA_FINANCE_URL: str = "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding"
UNISA_NSFAS_APPEAL_URL: str = "https://www.unisa.ac.za/sites/corporate/default/Apply-for-admission/Fees-&-funding/NSFAS"

# Application
APP_NAME: str = "UNISA AI Financial Aid Assistant"
APP_VERSION: str = "1.0.0"
