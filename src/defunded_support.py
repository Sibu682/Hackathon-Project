"""
Defunded Student Support module.

Displays a clear defunding notification, UNISA Student Finance contact details,
the formal appeals process, and links to institutional support channels.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from config.settings import (
    UNISA_FINANCE_EMAIL,
    UNISA_FINANCE_PHONE,
    UNISA_FINANCE_URL,
    UNISA_NSFAS_APPEAL_URL,
    NSFAS_HELPLINE,
    NSFAS_EMAIL,
    NSFAS_WEBSITE,
)

console = Console()


def render_defunded_support(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    """Display the full defunded-student support view."""
    console.print()
    console.rule("[bold red]Funding Status Alert[/bold red]", style="red")
    console.print()

    _render_defund_notice(student, assessment)
    _render_contact_details()
    _render_appeal_process(student)
    _render_support_channels()


# ---------------------------------------------------------------------------
# Defunding notice
# ---------------------------------------------------------------------------

def _render_defund_notice(student: dict[str, Any], assessment: dict[str, Any]) -> None:
    fs = student["funding_status"]
    name = student["personal_info"]["first_name"]
    defund_date = fs.get("defund_date", "Unknown")
    defund_reason = fs.get("defund_reason", "Reason not specified.")
    outstanding = assessment["outstanding_amount"]

    body = (
        f"[bold red]⛔ NSFAS Funding Discontinued[/bold red]\n\n"
        f"Dear [bold]{name}[/bold],\n\n"
        f"Our records show that your NSFAS bursary award has been discontinued "
        f"effective [bold]{defund_date}[/bold].\n\n"
        f"[bold]Stated reason on record:[/bold]\n"
        f"[italic]{defund_reason}[/italic]\n\n"
    )

    if outstanding > 0:
        body += (
            f"[bold]Outstanding balance:[/bold] [red]R{outstanding:,.2f}[/red]\n"
            "This amount is now your responsibility. Please contact UNISA Student "
            "Finance to discuss a payment arrangement or the appeals process.\n\n"
        )

    body += (
        "[dim]This notification is based on available records. "
        "If you believe this is an error, you have the right to query and appeal "
        "the decision through the channels listed below.[/dim]"
    )

    console.print(
        Panel(body, border_style="red", box=box.ROUNDED, title="[bold red]Defunding Notice[/bold red]")
    )
    console.print()


# ---------------------------------------------------------------------------
# Contact details
# ---------------------------------------------------------------------------

def _render_contact_details() -> None:
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim")
    table.add_column("Contact Point", style="bold")
    table.add_column("Details")

    table.add_row(
        "UNISA Student Finance — Phone",
        f"[cyan]{UNISA_FINANCE_PHONE}[/cyan]  (Mon–Fri, 08:00–16:00)",
    )
    table.add_row(
        "UNISA Student Finance — Email",
        f"[cyan]{UNISA_FINANCE_EMAIL}[/cyan]",
    )
    table.add_row(
        "UNISA Fees & Funding Portal",
        f"[link={UNISA_FINANCE_URL}][cyan]{UNISA_FINANCE_URL}[/cyan][/link]",
    )
    table.add_row(
        "NSFAS Helpline (toll-free)",
        f"[cyan]{NSFAS_HELPLINE}[/cyan]",
    )
    table.add_row(
        "NSFAS Email",
        f"[cyan]{NSFAS_EMAIL}[/cyan]",
    )
    table.add_row(
        "NSFAS Website",
        f"[link={NSFAS_WEBSITE}][cyan]{NSFAS_WEBSITE}[/cyan][/link]",
    )

    console.print(
        Panel(
            table,
            title="[bold]Contact Details[/bold]",
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()


# ---------------------------------------------------------------------------
# Appeal process
# ---------------------------------------------------------------------------

def _render_appeal_process(student: dict[str, Any]) -> None:
    fs = student["funding_status"]
    appeal_deadline = fs.get("appeal_deadline", "Contact UNISA Student Finance for the current deadline")

    steps = [
        (
            "1. Gather supporting documentation",
            "Collect your academic transcripts, proof of registration, "
            "NSFAS correspondence, and any documentation that supports your appeal "
            "(e.g. medical certificates, affidavits for extenuating circumstances).",
        ),
        (
            "2. Contact UNISA Student Finance",
            f"Reach out via phone ({UNISA_FINANCE_PHONE}) or email ({UNISA_FINANCE_EMAIL}) "
            "to confirm the specific appeal procedure applicable to your situation.",
        ),
        (
            "3. Submit a formal NSFAS appeal",
            f"Log into the NSFAS self-service portal at {NSFAS_APPLY_URL_DISPLAY()} "
            "and submit a formal appeal with your supporting documents.",
        ),
        (
            "4. Follow up regularly",
            "Track your appeal status on the NSFAS portal. Keep records of all "
            "correspondence. NSFAS typically responds within 15–30 business days.",
        ),
        (
            "5. Explore alternative funding",
            "While your appeal is in progress, consider applying for the UNISA "
            "Student Financial Aid Fund (SFAF) as emergency support, or explore "
            "bursary opportunities listed in your personalised recommendations.",
        ),
    ]

    body = f"[bold]Appeal deadline on record:[/bold] [yellow]{appeal_deadline}[/yellow]\n\n"
    body += f"[bold]NSFAS Appeal Portal:[/bold] [cyan link={UNISA_NSFAS_APPEAL_URL}]{UNISA_NSFAS_APPEAL_URL}[/cyan]\n\n"
    body += "[bold]Steps to query or appeal your defunding decision:[/bold]\n\n"

    for title, detail in steps:
        body += f"[bold cyan]{title}[/bold cyan]\n{detail}\n\n"

    console.print(
        Panel(
            body.strip(),
            title="[bold]Appeals & Query Process[/bold]",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )
    console.print()


def NSFAS_APPLY_URL_DISPLAY() -> str:
    return "https://my.nsfas.org.za"


# ---------------------------------------------------------------------------
# Institutional support channels
# ---------------------------------------------------------------------------

def _render_support_channels() -> None:
    channels = [
        ("UNISA Student Support Services", "https://www.unisa.ac.za/sites/corporate/default/Colleges/Student-support"),
        ("UNISA Advocacy & Support", "https://www.unisa.ac.za/sites/corporate/default/Colleges/Student-support/Advocacy"),
        ("UNISA Disability Unit", "https://www.unisa.ac.za/sites/corporate/default/Colleges/Student-support/Disability"),
        ("UNISA Student Counselling", "https://www.unisa.ac.za/sites/corporate/default/Colleges/Student-support/Counselling"),
    ]

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim")
    table.add_column("Support Channel", style="bold")
    table.add_column("URL")

    for name, url in channels:
        table.add_row(name, f"[cyan link={url}]{url}[/cyan]")

    console.print(
        Panel(
            table,
            title="[bold]Institutional Support Channels[/bold]",
            border_style="magenta",
            box=box.ROUNDED,
        )
    )
    console.print()
