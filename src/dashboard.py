"""
Financial Aid Dashboard — renders the funded student's full financial overview.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from rich.text import Text

console = Console()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_dashboard(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    """Render the full financial aid dashboard for a funded student."""
    console.print()
    console.rule("[bold cyan]Financial Aid Dashboard[/bold cyan]", style="cyan")
    console.print()

    _render_summary_card(student, assessment)
    _render_funding_status(student, assessment)
    _render_registration_status(student)
    _render_payment_history(student)
    _render_notifications(student, assessment)


# ---------------------------------------------------------------------------
# Summary card
# ---------------------------------------------------------------------------

def _render_summary_card(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    pi = student["personal_info"]
    ar = student["academic_record"]
    fs = student["funding_status"]

    balance = fs.get("outstanding_balance", 0.0)
    balance_colour = "red" if balance > 0 else "green"

    info_table = Table(box=None, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="dim", no_wrap=True)
    info_table.add_column("Value", style="bold")

    info_table.add_row("Student Number", student["student_id"])
    info_table.add_row("Full Name", f"{pi['first_name']} {pi['last_name']}")
    info_table.add_row("Email", pi["email"])
    info_table.add_row("Year of Study", str(ar["year_of_study"]))
    info_table.add_row("Academic Standing", ar["academic_standing"])
    info_table.add_row("GPA", f"{ar['gpa']}%")
    info_table.add_row(
        "Outstanding Balance",
        f"[{balance_colour}]R{balance:,.2f}[/{balance_colour}]",
    )

    console.print(
        Panel(
            info_table,
            title="[bold]Student Summary[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()


# ---------------------------------------------------------------------------
# Funding status section
# ---------------------------------------------------------------------------

def _render_funding_status(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    fs = student["funding_status"]
    is_funded = assessment["is_nsfas_funded"]
    is_defunded = assessment["is_defunded"]

    status_text = Text()
    if is_defunded:
        status_text.append("● DEFUNDED", style="bold red")
        status_text.append("  — Funding has been discontinued.", style="dim red")
    elif is_funded:
        status_text.append("● ACTIVE", style="bold green")
        status_text.append("  — NSFAS funding is current.", style="dim green")
    else:
        status_text.append("● NOT FUNDED", style="bold yellow")
        status_text.append("  — No active NSFAS award.", style="dim yellow")

    detail_table = Table(box=None, show_header=False, padding=(0, 2))
    detail_table.add_column("Field", style="dim", no_wrap=True)
    detail_table.add_column("Value")

    detail_table.add_row("NSFAS Status", status_text)
    detail_table.add_row(
        "Application Status",
        fs.get("nsfas_application_status", "Unknown"),
    )
    ref = fs.get("nsfas_reference_number") or "—"
    detail_table.add_row("Reference Number", ref)

    if is_defunded:
        detail_table.add_row(
            "Defund Date", fs.get("defund_date", "Unknown")
        )
        detail_table.add_row(
            "Appeal Deadline", fs.get("appeal_deadline", "Contact student finance")
        )

    outstanding = assessment["outstanding_amount"]
    colour = "red" if outstanding > 0 else "green"
    detail_table.add_row(
        "Outstanding Balance",
        f"[{colour}]R{outstanding:,.2f}[/{colour}]",
    )

    # Potential reasons if outstanding
    if assessment["has_outstanding_fees"] and assessment["potential_reasons"]:
        reasons_text = "\n".join(
            f"  [yellow]•[/yellow] {r}" for r in assessment["potential_reasons"]
        )
        detail_table.add_row(
            "Possible Reasons[dim]*[/dim]",
            reasons_text,
        )

    console.print(
        Panel(
            detail_table,
            title="[bold]NSFAS Funding Status[/bold]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    if assessment["has_outstanding_fees"]:
        console.print(
            "[dim]  * These are potential reasons only and have not been confirmed. "
            "Contact UNISA Student Finance for an official explanation.[/dim]"
        )

    console.print()


# ---------------------------------------------------------------------------
# Registration / qualification status
# ---------------------------------------------------------------------------

def _render_registration_status(student: dict[str, Any]) -> None:
    ar = student["academic_record"]
    fs = student["funding_status"]
    qualifications = ar.get("registered_qualifications", [])

    if not qualifications:
        console.print("[dim]No registered qualifications found.[/dim]")
        return

    for qual in qualifications:
        # Determine funding flag per qualification (multi-qual scenario has it on the qual)
        qual_funded = qual.get("nsfas_funded", fs.get("nsfas_funded", False))
        funded_label = (
            "[bold green]✓ NSFAS Funded[/bold green]"
            if qual_funded
            else "[bold yellow]✗ Not NSFAS Funded[/bold yellow]"
        )

        mod_table = Table(
            title="Registered Modules",
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style="bold dim",
        )
        mod_table.add_column("Code", style="cyan", no_wrap=True)
        mod_table.add_column("Module Name")
        mod_table.add_column("Credits", justify="center")
        mod_table.add_column("Result", justify="center")

        for mod in qual.get("modules_registered", []):
            result = mod["result"]
            if result is None:
                result_display = "[dim]Incomplete[/dim]"
            elif result >= 50:
                result_display = f"[green]{result}%[/green]"
            else:
                result_display = f"[red]{result}%[/red]"

            mod_table.add_row(
                mod["code"],
                mod["name"],
                str(mod["credits"]),
                result_display,
            )

        qual_info = (
            f"[bold]{qual['qualification_name']}[/bold]  ({qual['qualification_code']})\n"
            f"Enrolled: {qual['year_enrolled']}  ·  Status: {qual['status']}  ·  "
            f"Funding: {funded_label}\n"
        )

        if qual.get("funding_note"):
            qual_info += f"[dim italic]{qual['funding_note']}[/dim italic]\n"

        qual_info_text = Text.from_markup(qual_info)

        console.print(
            Panel(
                Columns([qual_info_text, mod_table], equal=False, expand=True),
                title="[bold]Qualification & Registration[/bold]",
                border_style="magenta",
                box=box.ROUNDED,
            )
        )
        console.print()


# ---------------------------------------------------------------------------
# Payment history
# ---------------------------------------------------------------------------

def _render_payment_history(student: dict[str, Any]) -> None:
    fs = student["funding_status"]
    history = fs.get("payment_history", [])

    if not history:
        return

    table = Table(
        title="Payment History",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
    )
    table.add_column("Date", style="dim", no_wrap=True)
    table.add_column("Description")
    table.add_column("Amount", justify="right")
    table.add_column("Status", justify="center")

    status_styles = {
        "Paid": "green",
        "Pending": "yellow",
        "Cancelled": "red",
        "Outstanding": "bold red",
    }

    for payment in history:
        status = payment["status"]
        style = status_styles.get(status, "white")
        amount_display = f"R{payment['amount']:,.2f}" if payment["amount"] > 0 else "—"
        table.add_row(
            payment["date"],
            payment["description"],
            amount_display,
            f"[{style}]{status}[/{style}]",
        )

    console.print(Panel(table, border_style="dim", box=box.ROUNDED))
    console.print()


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def _render_notifications(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    notifications: list[tuple[str, str]] = []

    if assessment["is_defunded"]:
        notifications.append((
            "critical",
            "Your NSFAS funding has been discontinued. "
            "You must contact UNISA Student Finance immediately to discuss an appeal.",
        ))

    if assessment["has_outstanding_fees"]:
        notifications.append((
            "warning",
            f"Your account has an outstanding balance of "
            f"R{assessment['outstanding_amount']:,.2f}. This may affect your "
            "registration and access to results. Please resolve this as soon as possible.",
        ))

    fs = student["funding_status"]
    if fs.get("appeal_deadline"):
        notifications.append((
            "info",
            f"Your NSFAS appeal deadline is {fs['appeal_deadline']}. "
            "Ensure you submit all required documentation before this date.",
        ))

    ar = student["academic_record"]
    if ar.get("academic_standing") == "Academic Risk":
        notifications.append((
            "warning",
            "Your academic standing is flagged as 'Academic Risk'. "
            "This may impact your funding eligibility. Contact your academic advisor.",
        ))

    # Multi-qual warning
    unfunded = fs.get("unfunded_qualifications", [])
    if unfunded:
        names = ", ".join(unfunded)
        notifications.append((
            "info",
            f"You are registered for more than one qualification. "
            f"NSFAS only funds one qualification at a time. "
            f"Qualification(s) [{names}] are not covered by your current NSFAS award. "
            "See the bursary recommendations section for alternative funding options.",
        ))

    if not notifications:
        return

    style_map = {
        "critical": ("bold red", "⛔"),
        "warning": ("bold yellow", "⚠"),
        "info": ("bold cyan", "ℹ"),
    }

    for level, message in notifications:
        colour, icon = style_map.get(level, ("white", "•"))
        console.print(
            Panel(
                f"[{colour}]{icon}[/{colour}]  {message}",
                border_style=colour.split()[-1],
                box=box.ROUNDED,
                expand=False,
            )
        )
    console.print()
