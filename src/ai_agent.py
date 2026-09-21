"""
AI Agent core — NSFAS funding detection and analysis.

Uses the OpenAI chat completions API (with tool/function calling) to reason
about a student's funding status and produce structured guidance.  When no
API key is configured the agent falls back to a deterministic rule-based
engine so the system is fully usable without an OpenAI account.
"""

from __future__ import annotations

import json
import os
from typing import Any

from rich.console import Console

console = Console()

# Lazy import — only needed when OpenAI key is present
_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
        _openai_client = OpenAI(api_key=api_key)
        return _openai_client
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Tool definitions for OpenAI function-calling
# ---------------------------------------------------------------------------

_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "assess_nsfas_status",
            "description": (
                "Determines whether a student is funded by NSFAS and what actions "
                "should be taken based on their current funding status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "is_nsfas_funded": {
                        "type": "boolean",
                        "description": "True if the student currently has an active NSFAS award.",
                    },
                    "is_defunded": {
                        "type": "boolean",
                        "description": "True if the student was previously funded but has been defunded.",
                    },
                    "has_outstanding_fees": {
                        "type": "boolean",
                        "description": "True if the student has an outstanding balance greater than zero.",
                    },
                    "outstanding_amount": {
                        "type": "number",
                        "description": "The rand value of outstanding fees (0 if none).",
                    },
                    "potential_reasons": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Possible (not confirmed) reasons for outstanding fees. "
                            "Must be framed as possibilities, never as confirmed facts."
                        ),
                    },
                    "recommended_action": {
                        "type": "string",
                        "enum": [
                            "apply_for_nsfas",
                            "view_dashboard",
                            "contact_student_finance",
                            "appeal_defunding",
                        ],
                        "description": "The primary recommended next step for the student.",
                    },
                    "summary_message": {
                        "type": "string",
                        "description": (
                            "A concise, empathetic plain-English summary of the student's "
                            "funding situation (2–4 sentences)."
                        ),
                    },
                },
                "required": [
                    "is_nsfas_funded",
                    "is_defunded",
                    "has_outstanding_fees",
                    "outstanding_amount",
                    "potential_reasons",
                    "recommended_action",
                    "summary_message",
                ],
            },
        },
    }
]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an AI Financial Aid Assistant for the University of South Africa (UNISA).
Your role is to analyse a student's funding data and provide clear, empathetic,
and factually accurate guidance about their NSFAS funding status.

IMPORTANT RULES:
1. Never assume a student has been defunded unless the data explicitly states it.
2. Never state that NSFAS has delayed a payment unless payment records confirm it.
3. Outstanding fees may have multiple potential causes — always frame them as
   possibilities, not confirmed facts.
4. Keep your language simple, supportive and accessible.
5. Always respond using the assess_nsfas_status tool — never with free text only.
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_funding_status(student: dict[str, Any]) -> dict[str, Any]:
    """
    Run the AI agent against a student record.

    Returns a structured assessment dict with keys:
        is_nsfas_funded, is_defunded, has_outstanding_fees,
        outstanding_amount, potential_reasons, recommended_action,
        summary_message.
    """
    client = _get_openai_client()

    if client:
        return _ai_assessment(client, student)
    else:
        console.print(
            "[dim yellow]ℹ No OpenAI API key found — using rule-based assessment.[/dim yellow]"
        )
        return _rule_based_assessment(student)


# ---------------------------------------------------------------------------
# OpenAI path
# ---------------------------------------------------------------------------

def _build_user_message(student: dict[str, Any]) -> str:
    fs = student["funding_status"]
    ar = student["academic_record"]
    name = student["personal_info"]["first_name"]

    qualifications = []
    for q in ar.get("registered_qualifications", []):
        funded_note = q.get("funding_note", "")
        nsfas_flag = q.get("nsfas_funded", None)
        if nsfas_flag is None:
            # Top-level funded student with single qual
            nsfas_flag = fs.get("nsfas_funded", False)
        qualifications.append(
            f"  - {q['qualification_name']} ({q['qualification_code']}): "
            f"NSFAS funded = {nsfas_flag}. {funded_note}"
        )

    payment_summary = []
    for p in fs.get("payment_history", [])[-3:]:
        payment_summary.append(
            f"  - {p['date']}: R{p['amount']:,.2f} — {p['status']} — {p['description']}"
        )

    return f"""Student profile for analysis:
Name: {name} {student['personal_info']['last_name']}
Student ID: {student['student_id']}
NSFAS application status: {fs.get('nsfas_application_status', 'Unknown')}
Currently NSFAS funded: {fs.get('nsfas_funded', False)}
Defunded: {fs.get('defunded', False)}
Defund reason: {fs.get('defund_reason', 'N/A')}
Outstanding balance: R{fs.get('outstanding_balance', 0):,.2f}
Academic standing: {ar.get('academic_standing', 'Unknown')}
GPA: {ar.get('gpa', 'N/A')}%

Registered qualifications:
{chr(10).join(qualifications) if qualifications else '  None'}

Recent payment history:
{chr(10).join(payment_summary) if payment_summary else '  No payment history'}

Please assess this student's NSFAS funding situation and call assess_nsfas_status."""


def _ai_assessment(client, student: dict[str, Any]) -> dict[str, Any]:
    """Call OpenAI and extract the structured tool result."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_message(student)},
            ],
            tools=_TOOLS,
            tool_choice={"type": "function", "function": {"name": "assess_nsfas_status"}},
            temperature=0.2,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        result = json.loads(tool_call.function.arguments)
        result["source"] = "ai"
        return result

    except Exception as exc:
        console.print(f"[yellow]AI assessment failed ({exc}), falling back to rules.[/yellow]")
        return _rule_based_assessment(student)


# ---------------------------------------------------------------------------
# Rule-based fallback
# ---------------------------------------------------------------------------

def _rule_based_assessment(student: dict[str, Any]) -> dict[str, Any]:
    """Deterministic assessment — no external API required."""
    fs = student["funding_status"]
    name = student["personal_info"]["first_name"]

    is_funded: bool = fs.get("nsfas_funded", False)
    is_defunded: bool = fs.get("defunded", False)
    outstanding: float = float(fs.get("outstanding_balance", 0.0))
    has_outstanding: bool = outstanding > 0.0

    potential_reasons: list[str] = fs.get("potential_outstanding_reasons", [])

    # Derive potential reasons from payment history when not already set
    if has_outstanding and not potential_reasons:
        for payment in fs.get("payment_history", []):
            if payment.get("status") in ("Pending", "Cancelled", "Outstanding"):
                potential_reasons.append(
                    f"A payment of R{payment['amount']:,.2f} dated {payment['date']} "
                    f"has a status of '{payment['status']}' — this may be contributing "
                    "to the outstanding balance."
                )
        if not potential_reasons:
            potential_reasons = [
                "The outstanding balance may be due to a pending NSFAS disbursement.",
                "There may be an administrative reconciliation delay.",
                "Additional module registrations may not yet be fully covered.",
            ]

    # Determine recommended action
    if is_defunded:
        action = "appeal_defunding"
    elif not is_funded:
        action = "apply_for_nsfas"
    elif has_outstanding:
        action = "contact_student_finance"
    else:
        action = "view_dashboard"

    # Build summary message
    if is_defunded:
        reason_snippet = fs.get("defund_reason", "")
        summary = (
            f"Hi {name}, your NSFAS funding has been discontinued. "
            f"According to available records: {reason_snippet} "
            "You have an outstanding balance that needs to be addressed. "
            "Please contact UNISA Student Finance to discuss your options and the appeals process."
        )
    elif not is_funded:
        summary = (
            f"Hi {name}, our records show that you are not currently funded by NSFAS. "
            "You may be eligible to apply — please visit the NSFAS website to check "
            "requirements and submit an application before the deadline."
        )
    elif has_outstanding:
        summary = (
            f"Hi {name}, you are funded by NSFAS, but your account shows an outstanding "
            f"balance of R{outstanding:,.2f}. There are a few possible reasons for this "
            "which are listed below. Please note these are potential causes and have not "
            "been confirmed — contact UNISA Student Finance for clarification."
        )
    else:
        summary = (
            f"Hi {name}, you are funded by NSFAS and your account is in good standing. "
            "Your financial aid dashboard below shows your current funding and registration details."
        )

    return {
        "is_nsfas_funded": is_funded,
        "is_defunded": is_defunded,
        "has_outstanding_fees": has_outstanding,
        "outstanding_amount": outstanding,
        "potential_reasons": potential_reasons,
        "recommended_action": action,
        "summary_message": summary,
        "source": "rules",
    }
