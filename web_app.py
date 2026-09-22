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

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, stream_with_context

from src.auth import authenticate
from src.ai_agent import analyse_funding_status, stream_funding_analysis
from src.bursary_recommender import recommend_bursaries, stream_bursary_recommendations
from src.alternative_funding import get_matched_partners, stream_alt_funding
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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
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


def _build_context(student: dict, assessment: dict | None = None, defer_funding: bool = True) -> dict:
    """Assemble all template context for a student.

    If *assessment* is provided (pre-computed or placeholder) it is used
    directly; otherwise the AI agent is invoked synchronously.  Passing a
    placeholder lets the dashboard route render the shell immediately while
    the real assessment streams in via SSE.

    When *defer_funding* is True (the default for the dashboard route),
    bursaries and alt_funding are returned as empty lists so the page shell
    renders instantly.  The /api/funding/stream SSE endpoint fills them in.
    """
    if assessment is None:
        assessment = analyse_funding_status(student)

    if defer_funding:
        bursaries   = []
        alt_funding = []
    else:
        bursaries   = recommend_bursaries(student)
        alt_funding = get_matched_partners(student)

    qualifications = student["academic_record"].get("registered_qualifications", [])
    is_multi_qual  = len(qualifications) > 1

    has_unfunded_quals = bool(student["funding_status"].get("unfunded_qualifications"))
    # show_alt_funding drives the sidebar link and section wrapper visibility.
    # We compute it from raw funding data so it is correct on first render
    # even before the SSE stream arrives.
    fs = student["funding_status"]
    show_alt_funding = (
        assessment["is_defunded"]
        or not assessment["is_nsfas_funded"]
        or assessment["has_outstanding_fees"]
        or has_unfunded_quals
        or float(fs.get("outstanding_balance", 0)) > 0
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

    # Build a lightweight placeholder assessment so the page shell renders
    # immediately.  The real AI assessment streams in via /api/agent/stream.
    fs = student["funding_status"]
    placeholder_assessment = {
        "is_nsfas_funded":    fs.get("nsfas_funded", False),
        "is_defunded":        fs.get("defunded", False),
        "has_outstanding_fees": float(fs.get("outstanding_balance", 0)) > 0,
        "outstanding_amount": float(fs.get("outstanding_balance", 0)),
        "potential_reasons":  [],
        "recommended_action": "view_dashboard",
        "summary_message":    "",   # blank — SSE will fill this
        "source":             "pending",
    }

    ctx = _build_context(student, assessment=placeholder_assessment, defer_funding=True)
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


@app.route("/api/agent/stream")
def api_agent_stream():
    """Server-Sent Events endpoint — streams the AI assessment word-by-word.

    Event types emitted:
        status  — progress/state messages ("analysing", "complete", "error")
        token   — a single word or punctuation chunk of the summary message
        result  — final JSON payload with the complete structured assessment
    """
    import json as _json

    from data import STUDENT_DATABASE_BY_ID
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "Not authenticated"}), 401
    student = STUDENT_DATABASE_BY_ID.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    def generate():
        # ── 1. Signal that the agent has started ────────────────────────
        yield "event: status\ndata: analysing\n\n"

        try:
            # ── 2. Stream tokens from the AI agent ───────────────────────
            final_assessment = None
            for chunk in stream_funding_analysis(student):
                event_type = chunk.get("type")

                if event_type == "token":
                    payload = _json.dumps({"token": chunk["token"]})
                    yield f"event: token\ndata: {payload}\n\n"

                elif event_type == "result":
                    final_assessment = chunk["result"]

            # ── 3. Emit the complete structured result ───────────────────
            if final_assessment:
                payload = _json.dumps(final_assessment)
                yield f"event: result\ndata: {payload}\n\n"

            # ── 4. Signal completion ─────────────────────────────────────
            yield "event: status\ndata: complete\n\n"

        except Exception as exc:
            error_payload = _json.dumps({"message": str(exc)})
            yield f"event: status\ndata: error\n\n"
            yield f"event: result\ndata: {error_payload}\n\n"

    response = Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/api/funding/stream")
def api_funding_stream():
    """Server-Sent Events endpoint — streams bursary and alt-funding results
    with word-by-word AI narrative per card.

    Event protocol:
        status      — "bursaries_start" | "altfunding_start" | "complete" | "error"
        count       — {"section": "bursaries"|"altfunding", "total": int}
        card_start  — {"section": str, "index": int, "data": dict}  shell metadata
        token       — {"section": str, "index": int, "token": str}  one word
        card_end    — {"section": str, "index": int}                narrative complete
    """
    import json as _json
    from src.ai_agent import stream_item_narrative
    from data import STUDENT_DATABASE_BY_ID

    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"error": "Not authenticated"}), 401
    student = STUDENT_DATABASE_BY_ID.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    def generate():
        try:
            # ── Bursaries ────────────────────────────────────────────────
            yield "event: status\ndata: bursaries_start\n\n"

            bursaries = stream_bursary_recommendations(student)
            bursary_items = []

            for chunk in bursaries:
                ctype = chunk["type"]

                if ctype == "count":
                    payload = _json.dumps({"section": "bursaries", "total": chunk["total"]})
                    yield f"event: count\ndata: {payload}\n\n"

                elif ctype == "bursary":
                    bursary_items.append(chunk)

                elif ctype == "done":
                    break

            # Stream each bursary card shell + narrative tokens
            for chunk in bursary_items:
                idx  = chunk["index"]
                data = chunk["data"]

                # 1. Send card shell (all metadata except description)
                shell = _json.dumps({"section": "bursaries", "index": idx, "data": data})
                yield f"event: card_start\ndata: {shell}\n\n"

                # 2. Stream narrative tokens word by word
                for tok in stream_item_narrative(student, data, "bursary"):
                    if tok["type"] == "token":
                        payload = _json.dumps({
                            "section": "bursaries",
                            "index":   idx,
                            "token":   tok["token"],
                        })
                        yield f"event: token\ndata: {payload}\n\n"

                # 3. Signal this card's narrative is complete
                yield f"event: card_end\ndata: {_json.dumps({'section': 'bursaries', 'index': idx})}\n\n"

            # ── Alternative funding ──────────────────────────────────────
            yield "event: status\ndata: altfunding_start\n\n"

            alt_items = []
            for chunk in stream_alt_funding(student):
                ctype = chunk["type"]

                if ctype == "count":
                    payload = _json.dumps({"section": "altfunding", "total": chunk["total"]})
                    yield f"event: count\ndata: {payload}\n\n"

                elif ctype == "partner":
                    alt_items.append(chunk)

                elif ctype == "done":
                    break

            for chunk in alt_items:
                idx  = chunk["index"]
                data = chunk["data"]

                shell = _json.dumps({"section": "altfunding", "index": idx, "data": data})
                yield f"event: card_start\ndata: {shell}\n\n"

                for tok in stream_item_narrative(student, data, "partner"):
                    if tok["type"] == "token":
                        payload = _json.dumps({
                            "section": "altfunding",
                            "index":   idx,
                            "token":   tok["token"],
                        })
                        yield f"event: token\ndata: {payload}\n\n"

                yield f"event: card_end\ndata: {_json.dumps({'section': 'altfunding', 'index': idx})}\n\n"

            # ── All done ─────────────────────────────────────────────────
            yield "event: status\ndata: complete\n\n"

        except Exception:
            import traceback
            traceback.print_exc()
            yield "event: status\ndata: error\n\n"

    response = Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
