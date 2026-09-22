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
import time
from typing import Any, Generator

from rich.console import Console

console = Console()

# Lazy import — only needed when Groq key is present
_groq_client = None


def _get_openai_client():
    """Return a Groq client (OpenAI-compatible).

    Groq exposes the same chat completions interface as OpenAI, so the
    existing tool-calling and streaming code works without any changes.
    The openai SDK is pointed at Groq's base URL with the Groq API key.
    """
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
        _groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return _groq_client
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
            "[dim yellow]ℹ No Groq API key found — using rule-based assessment.[/dim yellow]"
        )
        return _rule_based_assessment(student)


def stream_funding_analysis(student: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """
    Streaming version of the AI agent analysis.

    Yields dicts of two shapes:
        {"type": "token",  "token":  <str>}   — one word/punctuation chunk
        {"type": "result", "result": <dict>}  — final complete assessment

    The OpenAI path uses the streaming chat completions API so tokens arrive
    from the model in real time.  The rule-based path simulates streaming by
    emitting words with a small delay, giving the same progressive UX without
    requiring an API key.
    """
    client = _get_openai_client()

    if client:
        yield from _stream_ai_assessment(client, student)
    else:
        console.print(
            "[dim yellow]ℹ No Groq API key found — streaming rule-based assessment.[/dim yellow]"
        )
        yield from _stream_rule_based_assessment(student)


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


# ---------------------------------------------------------------------------
# Streaming helpers
# ---------------------------------------------------------------------------

def _stream_ai_assessment(
    client, student: dict[str, Any]
) -> Generator[dict[str, Any], None, None]:
    """
    Calls OpenAI with streaming enabled.

    Because the model is forced to call the `assess_nsfas_status` tool, the
    streamed content arrives as function-call argument deltas.  We accumulate
    the full JSON, then parse it at the end.  While accumulating we emit
    word-level tokens extracted from the `summary_message` field as it grows,
    giving a real-time typing effect.
    """
    try:
        stream = client.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": _build_user_message(student)},
            ],
            tools=_TOOLS,
            tool_choice={"type": "function", "function": {"name": "assess_nsfas_status"}},
            temperature=0.2,
            stream=True,
        )

        accumulated_args = ""
        emitted_summary_len = 0  # how many chars of summary_message we've already tokenised

        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            tool_calls = getattr(delta, "tool_calls", None)
            if not tool_calls:
                continue

            fragment = tool_calls[0].function.arguments or ""
            accumulated_args += fragment

            # Try to extract the summary_message value as it streams in and
            # emit new words progressively.
            try:
                # Look for the summary_message string value inside the partial JSON.
                # We search for the key and then walk the characters after the colon.
                key_marker = '"summary_message"'
                key_idx = accumulated_args.find(key_marker)
                if key_idx != -1:
                    after_key = accumulated_args[key_idx + len(key_marker):]
                    # Find the opening quote of the value
                    colon_idx = after_key.find(":")
                    if colon_idx != -1:
                        after_colon = after_key[colon_idx + 1:].lstrip()
                        if after_colon.startswith('"'):
                            # Extract characters until either the closing quote or end
                            value_chars = []
                            escape_next = False
                            for ch in after_colon[1:]:
                                if escape_next:
                                    value_chars.append(ch)
                                    escape_next = False
                                elif ch == "\\":
                                    escape_next = True
                                elif ch == '"':
                                    break
                                else:
                                    value_chars.append(ch)

                            current_summary = "".join(value_chars)
                            new_text = current_summary[emitted_summary_len:]

                            if new_text:
                                # Split on whitespace boundaries and emit word tokens
                                words = new_text.split(" ")
                                for i, word in enumerate(words):
                                    if not word:
                                        continue
                                    # Don't emit a trailing partial word (no space yet)
                                    if i == len(words) - 1 and not new_text.endswith(" "):
                                        break
                                    yield {"type": "token", "token": word + " "}
                                    emitted_summary_len += len(word) + 1
            except Exception:
                pass  # partial JSON — keep accumulating

        # Parse the final complete JSON and emit any remaining summary tokens
        try:
            result = json.loads(accumulated_args)
            final_summary = result.get("summary_message", "")
            remaining = final_summary[emitted_summary_len:]
            if remaining.strip():
                words = remaining.split()
                for word in words:
                    yield {"type": "token", "token": word + " "}

            result["source"] = "ai"
            yield {"type": "result", "result": result}
        except Exception as parse_exc:
            console.print(f"[yellow]Stream parse failed ({parse_exc}), falling back.[/yellow]")
            yield from _stream_rule_based_assessment(student)

    except Exception as exc:
        console.print(f"[yellow]AI stream failed ({exc}), falling back to rules.[/yellow]")
        yield from _stream_rule_based_assessment(student)


def _stream_rule_based_assessment(
    student: dict[str, Any]
) -> Generator[dict[str, Any], None, None]:
    """
    Runs the rule-based assessment and simulates a streaming typing effect by
    emitting the summary message word-by-word with small delays.
    """
    result = _rule_based_assessment(student)
    summary = result.get("summary_message", "")

    words = summary.split()
    for i, word in enumerate(words):
        # Vary the delay slightly so it feels organic, not robotic
        delay = 0.045 if i % 5 != 0 else 0.08
        time.sleep(delay)
        yield {"type": "token", "token": word + " "}

    yield {"type": "result", "result": result}
