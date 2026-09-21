"""
UNISA AI Financial Aid Assistant — Flask Web Application
=========================================================
Run:  python3 web_app.py
Open: http://localhost:5000

Login with your student number (e.g. 53012345) and password.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from src.auth import authenticate
from src.ai_agent import analyse_funding_status
from src.bursary_recommender import recommend_bursaries
from src.alternative_funding import get_matched_partners
from config.settings import (
    APP_NAME, APP_VERSION,
    NSFAS_WEBSITE, NSFAS_APPLY_URL, NSFAS_HELPLINE, NSFAS_PHONE_ALT, NSFAS_EMAIL,
    UNISA_CONTACT_CENTRE, UNISA_FINANCE_EMAIL, UNISA_FINANCE_URL,
    UNISA_NSFAS_APPEAL_URL, UNISA_CONTACT_URL,
)
from data import (
    STUDENT_NOT_FUNDED, STUDENT_FUNDED_WITH_OUTSTANDING,
    STUDENT_MULTI_QUALIFICATION, STUDENT_DEFUNDED,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nsfas-hackathon-dev-secret-2026")

# ---------------------------------------------------------------------------
# Shared context
# ---------------------------------------------------------------------------

DEMO_SCENARIOS = {
    "not_funded":              STUDENT_NOT_FUNDED,
    "funded_with_outstanding": STUDENT_FUNDED_WITH_OUTSTANDING,
    "multi_qualification":     STUDENT_MULTI_QUALIFICATION,
    "defunded":                STUDENT_DEFUNDED,
}

CONTACTS = {
    "nsfas_website":         NSFAS_WEBSITE,
    "nsfas_apply_url":       NSFAS_APPLY_URL,
    "nsfas_helpline":        NSFAS_HELPLINE,
    "nsfas_phone_alt":       NSFAS_PHONE_ALT,
    "nsfas_email":           NSFAS_EMAIL,
    "unisa_contact_centre":  UNISA_CONTACT_CENTRE,
    "unisa_finance_email":   UNISA_FINANCE_EMAIL,
    "unisa_finance_url":     UNISA_FINANCE_URL,
    "unisa_nsfas_appeal_url":UNISA_NSFAS_APPEAL_URL,
    "unisa_contact_url":     UNISA_CONTACT_URL,
    "app_name":              APP_NAME,
    "app_version":           APP_VERSION,
}


def _build_context(student: dict) -> dict:
    """Run AI agent and assemble all template context for a student."""
    assessment  = analyse_funding_status(student)
    bursaries   = recommend_bursaries(student)
    alt_funding = get_matched_partners(student)

    qualifications = student["academic_record"].get("registered_qualifications", [])
    is_multi_qual  = len(qualifications) > 1

    has_unfunded_quals = bool(student["funding_status"].get("unfunded_qualifications"))
    show_alt_funding = (
        assessment["is_defunded"]
        or not assessment["is_nsfas_funded"]
        or assessment["has_outstanding_fees"]
        or has_unfunded_quals
    )

    return {
        "student":         student,
        "assessment":      assessment,
        "bursaries":       bursaries,
        "alt_funding":     alt_funding,
        "is_multi_qual":   is_multi_qual,
        "show_alt_funding":show_alt_funding,
        **CONTACTS,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if "student_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        student_number = request.form.get("student_number", "").strip()
        password       = request.form.get("password", "")
        student = authenticate(student_number, password)
        if student:
            session["student_id"] = student["student_id"]
            return redirect(url_for("dashboard"))
        error = "Incorrect student number or password. Please try again."

    return render_template("login.html", error=error, **CONTACTS)


@app.route("/demo/<scenario>")
def demo(scenario: str):
    student = DEMO_SCENARIOS.get(scenario)
    if not student:
        return redirect(url_for("login"))
    session["student_id"] = student["student_id"]
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    from data import STUDENT_DATABASE_BY_ID
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("login"))
    student = STUDENT_DATABASE_BY_ID.get(student_id)
    if not student:
        session.clear()
        return redirect(url_for("login"))

    ctx = _build_context(student)
    assessment = ctx["assessment"]

    if assessment["is_defunded"]:
        template = "defunded.html"
    elif assessment["is_nsfas_funded"]:
        template = "dashboard.html"
    else:
        template = "not_funded.html"

    return render_template(template, **ctx)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/assess")
def api_assess():
    from data import STUDENT_DATABASE_BY_ID
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "Not authenticated"}), 401
    student = STUDENT_DATABASE_BY_ID.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(analyse_funding_status(student))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
