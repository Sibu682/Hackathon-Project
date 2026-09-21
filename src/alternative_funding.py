"""
Alternative Financial Aid module.

Matches and displays UNISA-partnered and government alternative funding
schemes based on the student's academic and financial profile.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from data import ALTERNATIVE_FUNDING_PARTNERS

console = Console()


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def _match_partners(student: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter and return alternative funding partners relevant to this student."""
    income = student["financial_profile"].get("household_income", 0)
    is_nsfas_funded = student["funding_status"].get("nsfas_funded", False)

    matched: list[dict[str, Any]] = []

    for partner in ALTERNATIVE_FUNDING_PARTNERS:
        # ISFAP targets the 'missing middle' — skip if NSFAS-funded (unless defunded)
        if partner["id"] == "AF001":
            threshold = partner.get("income_threshold", 600_000)
            if is_nsfas_funded and not student["funding_status"].get("defunded", False):
                continue  # ISFAP is for non-NSFAS students
            if threshold and income > threshold:
                continue  # over income cap

        # UNISA SFAF — emergency aid, most applicable when outstanding balance exists
        if partner["id"] == "AF002":
            outstanding = student["funding_status"].get("outstanding_balance", 0)
            if outstanding == 0 and is_nsfas_funded:
                continue  # not in financial distress

        matched.append(partner)

    return matched


# ---------------------------------------------------------------------------
# Public rendering function
# ---------------------------------------------------------------------------

def render_alternative_funding(student: dict[str, Any]) -> None:
    """Display alternative funding options matched to the student."""
    partners = _match_partners(student)

    console.print()
    console.rule(
        "[bold blue]Alternative Financial Aid Opportunities[/bold blue]", style="blue"
    )
    console.print()

    if not partners:
        console.print(
            Panel(
                "[dim]No alternative funding schemes matched your current profile.\n"
                "This may mean you are fully funded or do not currently meet the "
                "eligibility criteria of available schemes.[/dim]",
                border_style="dim",
                box=box.ROUNDED,
            )
        )
        console.print()
        return

    name = student["personal_info"]["first_name"]

    console.print(
        Panel(
            f"Based on [bold]{name}'s[/bold] financial profile and registration status, "
            "the following alternative funding opportunities may be available.\n\n"
            "[dim]Eligibility is determined by each scheme individually. "
            "UNISA does not guarantee approval. Apply as early as possible "
            "as funding is limited and subject to availability.[/dim]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()

    for partner in partners:
        _render_partner_card(partner)


def _render_partner_card(partner: dict[str, Any]) -> None:
    eligibility_list = "\n".join(
        f"  [dim cyan]•[/dim cyan] {req}"
        for req in partner.get("eligibility", [])
    )

    income_note = ""
    if partner.get("income_threshold"):
        income_note = (
            f"[bold]Income threshold:[/bold]  "
            f"Up to R{partner['income_threshold']:,} household income per annum\n"
        )

    body = (
        f"[bold]{partner['name']}[/bold]  "
        f"·  [dim]Type: {partner['type']}[/dim]\n\n"
        f"{partner['description']}\n\n"
        f"[bold]Eligibility requirements:[/bold]\n{eligibility_list}\n\n"
        f"{income_note}"
        f"[bold]Deadline:[/bold]   [yellow]{partner['deadline']}[/yellow]\n"
        f"[bold]Apply:[/bold]      [cyan link={partner['application_url']}]{partner['application_url']}[/cyan]\n"
        f"[bold]Contact:[/bold]    [cyan]{partner['contact_email']}[/cyan]"
    )

    console.print(
        Panel(
            body,
            title=f"[bold]{partner['name']}[/bold]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()
