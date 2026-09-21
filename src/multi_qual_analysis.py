"""
Multi-Qualification Funding Analysis module.

When a student is registered for more than one qualification this module
produces a detailed breakdown showing which qualification is NSFAS-funded,
which is not, and any eligibility warnings that apply.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def render_multi_qual_analysis(student: dict[str, Any]) -> None:
    """
    Display a per-qualification funding breakdown.
    Only called when the student has more than one registered qualification.
    """
    ar = student["academic_record"]
    fs = student["funding_status"]
    qualifications = ar.get("registered_qualifications", [])

    if len(qualifications) <= 1:
        return  # nothing to do

    console.print()
    console.rule("[bold magenta]Multi-Qualification Funding Analysis[/bold magenta]", style="magenta")
    console.print()

    _render_overview(student, qualifications, fs)
    _render_per_qual_breakdown(qualifications, fs)
    _render_eligibility_warnings(student, qualifications, fs)


# ---------------------------------------------------------------------------
# Overview panel
# ---------------------------------------------------------------------------

def _render_overview(
    student: dict[str, Any],
    qualifications: list[dict],
    fs: dict[str, Any],
) -> None:
    name = student["personal_info"]["first_name"]
    funded_code = fs.get("funded_qualification", "")
    unfunded_codes = fs.get("unfunded_qualifications", [])

    funded_names = [
        q["qualification_name"]
        for q in qualifications
        if q["qualification_code"] == funded_code
    ]
    unfunded_names = [
        q["qualification_name"]
        for q in qualifications
        if q["qualification_code"] in unfunded_codes
    ]

    funded_str = funded_names[0] if funded_names else "None"
    unfunded_str = ", ".join(unfunded_names) if unfunded_names else "None"

    body = (
        f"[bold]{name}[/bold], you are currently registered for "
        f"[bold]{len(qualifications)}[/bold] qualifications.\n\n"
        "NSFAS policy limits funding to [bold]one qualification per student[/bold] "
        "at a time. The table below shows which of your qualifications is covered "
        "and which requires alternative funding.\n\n"
        f"[bold]NSFAS-funded qualification:[/bold]  [green]{funded_str}[/green]\n"
        f"[bold]Not covered by NSFAS:[/bold]         [yellow]{unfunded_str}[/yellow]"
    )

    console.print(
        Panel(body, title="[bold]Overview[/bold]", border_style="magenta", box=box.ROUNDED)
    )
    console.print()


# ---------------------------------------------------------------------------
# Per-qualification breakdown table
# ---------------------------------------------------------------------------

def _render_per_qual_breakdown(
    qualifications: list[dict],
    fs: dict[str, Any],
) -> None:
    table = Table(
        title="Qualification Funding Breakdown",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
    )
    table.add_column("Code", style="cyan", no_wrap=True)
    table.add_column("Qualification Name")
    table.add_column("NQF Level", justify="center")
    table.add_column("Year Enrolled", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("NSFAS Funded", justify="center")

    for qual in qualifications:
        is_funded = qual.get("nsfas_funded", False)
        funded_display = (
            "[bold green]✓ Yes[/bold green]"
            if is_funded
            else "[bold yellow]✗ No[/bold yellow]"
        )
        status_colour = "green" if qual["status"] == "Active" else "red"

        table.add_row(
            qual["qualification_code"],
            qual["qualification_name"],
            "—",                          # NQF from catalogue; not duplicated here
            str(qual["year_enrolled"]),
            f"[{status_colour}]{qual['status']}[/{status_colour}]",
            funded_display,
        )

    console.print(Panel(table, border_style="blue", box=box.ROUNDED))
    console.print()


# ---------------------------------------------------------------------------
# Eligibility & funding limitation warnings
# ---------------------------------------------------------------------------

def _render_eligibility_warnings(
    student: dict[str, Any],
    qualifications: list[dict],
    fs: dict[str, Any],
) -> None:
    warnings: list[str] = []

    unfunded_codes = fs.get("unfunded_qualifications", [])
    unfunded_quals = [q for q in qualifications if q["qualification_code"] in unfunded_codes]

    for qual in unfunded_quals:
        warnings.append(
            f"[bold yellow]⚠ {qual['qualification_name']} ({qual['qualification_code']})[/bold yellow]\n"
            f"   {qual.get('funding_note', 'This qualification is not covered by NSFAS.')}\n"
            "   You should explore bursary and alternative funding options for this qualification."
        )

    ar = student["academic_record"]
    if ar.get("academic_standing") == "Academic Risk":
        warnings.append(
            "[bold red]⛔ Academic Standing — At Risk[/bold red]\n"
            "   Your academic standing may affect your continued NSFAS eligibility "
            "across all registered qualifications. Please contact your academic advisor."
        )

    if not warnings:
        console.print("[dim green]✓ No funding limitation warnings at this time.[/dim green]\n")
        return

    for warning in warnings:
        console.print(
            Panel(warning, border_style="yellow", box=box.ROUNDED, expand=False)
        )

    console.print()
