"""
Personalised Bursary Recommendation Engine.

Matches a student's academic profile against the bursary catalogue and
returns ranked, filtered recommendations with eligibility notes.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from data import BURSARY_CATALOGUE

console = Console()


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def _get_student_fields(student: dict[str, Any]) -> set[str]:
    """Collect all fields of study from the student's registered qualifications."""
    fields: set[str] = set()
    for qual in student["academic_record"].get("registered_qualifications", []):
        # Map qualification name keywords to catalogue field labels
        name = qual["qualification_name"].lower()
        if "commerce" in name:
            fields.add("Commerce")
        if "information technology" in name or "it" in name:
            fields.add("Information Technology")
        if "political" in name or "arts" in name:
            fields.add("Humanities")
        if "law" in name or "llb" in name:
            fields.add("Law")
        if "business" in name or "diploma" in name:
            fields.add("Business Administration")
        if "science" in name and "information" not in name:
            fields.add("Science")
        if "accounting" in name:
            fields.add("Accounting")
        if "finance" in name:
            fields.add("Finance")
        if "engineering" in name:
            fields.add("Engineering")

    return fields


def _get_unfunded_fields(student: dict[str, Any]) -> set[str]:
    """Return fields of study for qualifications not covered by NSFAS."""
    fs = student["funding_status"]
    unfunded_codes = fs.get("unfunded_qualifications", [])

    # If no explicit unfunded list, check per-qual flag
    unfunded_quals = []
    for qual in student["academic_record"].get("registered_qualifications", []):
        code = qual["qualification_code"]
        per_qual_funded = qual.get("nsfas_funded", None)

        if unfunded_codes and code in unfunded_codes:
            unfunded_quals.append(qual)
        elif per_qual_funded is False:
            unfunded_quals.append(qual)
        elif not fs.get("nsfas_funded", False):
            # Entirely unfunded student — all quals are unfunded
            unfunded_quals.append(qual)

    fields: set[str] = set()
    for qual in unfunded_quals:
        name = qual["qualification_name"].lower()
        if "commerce" in name:
            fields.add("Commerce")
        if "information technology" in name:
            fields.add("Information Technology")
        if "political" in name or "arts" in name:
            fields.add("Humanities")
        if "law" in name or "llb" in name:
            fields.add("Law")
        if "business" in name or "diploma" in name:
            fields.add("Business Administration")
        if "science" in name and "information" not in name:
            fields.add("Science")
        if "accounting" in name:
            fields.add("Accounting")
        if "finance" in name:
            fields.add("Finance")

    return fields


def _score_bursary(bursary: dict[str, Any], student: dict[str, Any]) -> tuple[int, list[str]]:
    """
    Score a bursary against a student profile.

    Returns (score, list_of_matched_criteria).
    Higher score = better match.
    """
    score = 0
    matched: list[str] = []
    eligibility_issues: list[str] = []

    gpa = student["academic_record"].get("gpa", 0)
    income = student["financial_profile"].get("household_income", 999_999)
    fields = _get_student_fields(student)

    # Field of study match (required)
    bursary_fields = set(bursary["fields_of_study"])
    if "All" in bursary_fields or (fields & bursary_fields):
        score += 30
        matched.append("Field of study matches")
    else:
        return -1, []  # hard filter — not eligible

    # GPA
    min_gpa = bursary.get("min_gpa", 0)
    if gpa >= min_gpa:
        score += 20
        matched.append(f"GPA {gpa}% meets minimum {min_gpa}%")
    else:
        eligibility_issues.append(f"GPA {gpa}% is below minimum {min_gpa}%")
        score -= 10

    # Financial need
    if bursary.get("financial_need_required"):
        threshold = 350_000
        if income <= threshold:
            score += 20
            matched.append("Financial need requirement met")
        else:
            eligibility_issues.append(
                f"Household income R{income:,} may exceed the financial need threshold"
            )
            score -= 5

    # Nationality
    nationality = student["personal_info"].get("nationality", "")
    if nationality in bursary.get("nationality", ["South African"]) or \
            "Other" in bursary.get("nationality", []):
        score += 10
        matched.append("Nationality eligible")

    # Upcoming deadline bonus
    deadline = bursary.get("deadline", "")
    if deadline and deadline >= "2026-09-21":
        score += 5
        matched.append("Application deadline is upcoming")

    return score, matched


def recommend_bursaries(student: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return a ranked list of bursary recommendations for the student.
    Only bursaries relevant to unfunded qualifications are included.
    """
    unfunded_fields = _get_unfunded_fields(student)

    # If there are no unfunded fields, check if the student is wholly unfunded
    if not unfunded_fields:
        if not student["funding_status"].get("nsfas_funded", False):
            unfunded_fields = _get_student_fields(student)

    if not unfunded_fields:
        return []

    recommendations: list[tuple[int, dict, list[str]]] = []

    for bursary in BURSARY_CATALOGUE:
        # Check if bursary covers any unfunded field
        bursary_fields = set(bursary["fields_of_study"])
        if "All" not in bursary_fields and not (unfunded_fields & bursary_fields):
            continue  # bursary doesn't apply to unfunded qualifications

        score, matched = _score_bursary(bursary, student)
        if score >= 0:
            recommendations.append((score, bursary, matched))

    recommendations.sort(key=lambda x: x[0], reverse=True)
    return [
        {**bursary, "_score": score, "_matched_criteria": matched}
        for score, bursary, matched in recommendations
    ]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_bursary_recommendations(student: dict[str, Any]) -> None:
    """Display personalised bursary recommendations."""
    recommendations = recommend_bursaries(student)

    console.print()
    console.rule(
        "[bold green]Personalised Bursary Recommendations[/bold green]", style="green"
    )
    console.print()

    if not recommendations:
        console.print(
            Panel(
                "[dim]No bursary matches found for your current profile and unfunded qualifications.\n"
                "Check back as new bursaries are regularly added.[/dim]",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
        console.print()
        return

    name = student["personal_info"]["first_name"]
    unfunded_fields = _get_unfunded_fields(student) or _get_student_fields(student)
    fields_str = ", ".join(sorted(unfunded_fields))

    console.print(
        Panel(
            f"The following bursaries were matched to [bold]{name}'s[/bold] profile "
            f"based on field of study ([italic]{fields_str}[/italic]), academic results, "
            "and financial need.\n\n"
            "[dim]Eligibility and funding availability are subject to each funder's "
            "requirements. Verify all details directly with the funder before applying.[/dim]",
            border_style="green",
            box=box.ROUNDED,
        )
    )
    console.print()

    for idx, rec in enumerate(recommendations, start=1):
        _render_bursary_card(idx, rec)


def _render_bursary_card(rank: int, bursary: dict[str, Any]) -> None:
    score = bursary.pop("_score", 0)
    matched = bursary.pop("_matched_criteria", [])

    match_str = "  ".join(f"[dim green]✓ {m}[/dim green]" for m in matched)

    body = (
        f"[bold]{bursary['name']}[/bold]  ·  [dim]Funder: {bursary['funder']}[/dim]\n\n"
        f"{bursary['description']}\n\n"
        f"[bold]Award amount:[/bold]  R{bursary['amount']:,} per year\n"
        f"[bold]Deadline:[/bold]     [yellow]{bursary['deadline']}[/yellow]\n"
        f"[bold]Apply:[/bold]        [cyan link={bursary['application_url']}]{bursary['application_url']}[/cyan]\n\n"
        f"[bold]Matched criteria:[/bold]\n{match_str}"
    )

    console.print(
        Panel(
            body,
            title=f"[bold]#{rank} — {bursary['name']}[/bold]",
            border_style="green",
            box=box.ROUNDED,
        )
    )
    console.print()
