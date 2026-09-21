"""
UNISA AI-Powered Student Funding & Financial Assistance System
==============================================================
Main application entry point.

Run:
    python main.py

For demo mode (skip login, pick a scenario directly):
    python main.py --demo
"""

from __future__ import annotations

import argparse
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
import questionary

from config.settings import (
    APP_NAME,
    APP_VERSION,
    NSFAS_WEBSITE,
    NSFAS_APPLY_URL,
    NSFAS_HELPLINE,
    NSFAS_EMAIL,
    UNISA_FINANCE_EMAIL,
    UNISA_FINANCE_PHONE,
)
from src.auth import login_prompt
from src.ai_agent import analyse_funding_status
from src.dashboard import render_dashboard
from src.defunded_support import render_defunded_support
from src.multi_qual_analysis import render_multi_qual_analysis
from src.bursary_recommender import render_bursary_recommendations
from src.alternative_funding import render_alternative_funding
from data import (
    STUDENT_NOT_FUNDED,
    STUDENT_FUNDED_WITH_OUTSTANDING,
    STUDENT_MULTI_QUALIFICATION,
    STUDENT_DEFUNDED,
)

console = Console()


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

def _print_banner() -> None:
    console.clear()
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{APP_NAME}[/bold cyan]\n"
            f"[dim]Version {APP_VERSION}  ·  Powered by AI[/dim]\n\n"
            "[dim]This system helps UNISA students understand their NSFAS\n"
            "funding status and discover alternative financial aid opportunities.[/dim]",
            box=box.DOUBLE,
            border_style="cyan",
            expand=False,
        )
    )
    console.print()


# ---------------------------------------------------------------------------
# Not-funded flow
# ---------------------------------------------------------------------------

def _handle_not_funded(student: dict) -> None:
    name = student["personal_info"]["first_name"]

    console.print()
    console.print(
        Panel(
            f"[bold yellow]⚠  You are not currently funded by NSFAS[/bold yellow]\n\n"
            f"Hi [bold]{name}[/bold], our records show that you do not have an active "
            "NSFAS bursary award.\n\n"
            "You may be eligible to apply. NSFAS provides funding to South African "
            "students from households with a combined income of up to R350 000 per year.\n\n"
            f"[bold]Apply now:[/bold]     [cyan link={NSFAS_APPLY_URL}]{NSFAS_APPLY_URL}[/cyan]\n"
            f"[bold]NSFAS website:[/bold] [cyan link={NSFAS_WEBSITE}]{NSFAS_WEBSITE}[/cyan]\n"
            f"[bold]Helpline:[/bold]      [cyan]{NSFAS_HELPLINE}[/cyan] (toll-free)\n"
            f"[bold]Email:[/bold]         [cyan]{NSFAS_EMAIL}[/cyan]\n\n"
            "[bold]Key application requirements:[/bold]\n"
            "  • South African citizen or permanent resident\n"
            "  • Combined household income ≤ R350 000 per annum\n"
            "  • Registered (or applying to register) at a public university\n"
            "  • Valid South African ID number\n"
            "  • Grade 12 / matric certificate\n\n"
            "[dim]Application windows typically open in September each year for the "
            "following academic year. Check the NSFAS website for current deadlines.[/dim]",
            title="[bold yellow]NSFAS Application Required[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )
    console.print()

    # Still show bursary & alternative funding options
    render_bursary_recommendations(student)
    render_alternative_funding(student)


# ---------------------------------------------------------------------------
# Funded flow (with or without outstanding fees)
# ---------------------------------------------------------------------------

def _handle_funded(student: dict, assessment: dict) -> None:
    # Main dashboard
    render_dashboard(student, assessment)

    # Multi-qualification analysis if applicable
    qualifications = student["academic_record"].get("registered_qualifications", [])
    if len(qualifications) > 1:
        render_multi_qual_analysis(student)

    # Bursaries for unfunded qualifications
    render_bursary_recommendations(student)

    # Alternative funding if there are outstanding fees or unfunded quals
    has_unfunded = bool(student["funding_status"].get("unfunded_qualifications"))
    if assessment["has_outstanding_fees"] or has_unfunded:
        render_alternative_funding(student)


# ---------------------------------------------------------------------------
# Defunded flow
# ---------------------------------------------------------------------------

def _handle_defunded(student: dict, assessment: dict) -> None:
    # Dashboard first so student can see their record
    render_dashboard(student, assessment)

    # Detailed defunding support
    render_defunded_support(student, assessment)

    # Bursary and alternative options while appeal is in progress
    render_bursary_recommendations(student)
    render_alternative_funding(student)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run(student: dict) -> None:
    """
    Core application flow for an authenticated student.
    The AI agent analyses the student's data and routes
    them to the appropriate set of views.
    """
    console.print("[dim]Analysing your funding status…[/dim]")
    assessment = analyse_funding_status(student)

    console.print()
    console.print(
        Panel(
            f"[bold]AI Assessment[/bold]\n\n{assessment['summary_message']}",
            border_style="cyan",
            box=box.ROUNDED,
            title="[bold]Funding Status Summary[/bold]",
        )
    )
    console.print()

    # Route based on assessment
    if assessment["is_defunded"]:
        _handle_defunded(student, assessment)
    elif assessment["is_nsfas_funded"]:
        _handle_funded(student, assessment)
    else:
        _handle_not_funded(student)

    _print_footer()


def _print_footer() -> None:
    console.print()
    console.rule("[dim]End of Report[/dim]", style="dim")
    console.print(
        "\n[dim]For further assistance contact UNISA Student Finance:\n"
        f"  Phone: {UNISA_FINANCE_PHONE}  ·  Email: {UNISA_FINANCE_EMAIL}[/dim]\n"
    )


# ---------------------------------------------------------------------------
# Demo mode — scenario picker
# ---------------------------------------------------------------------------

_DEMO_SCENARIOS: dict[str, dict] = {
    "Scenario 1 — Student NOT funded by NSFAS  (Thabo Mokoena)": STUDENT_NOT_FUNDED,
    "Scenario 2 — Funded by NSFAS WITH outstanding fees  (Lerato Dlamini)": STUDENT_FUNDED_WITH_OUTSTANDING,
    "Scenario 3 — Registered for MORE THAN ONE qualification  (Naledi Sithole)": STUDENT_MULTI_QUALIFICATION,
    "Scenario 4 — DEFUNDED student  (Sipho Nkosi)": STUDENT_DEFUNDED,
}


def demo_mode() -> None:
    """Interactive scenario picker for demonstration purposes."""
    _print_banner()

    console.print(
        Panel(
            "[bold yellow]DEMO MODE[/bold yellow]\n"
            "Select a simulation scenario to explore. "
            "No login credentials are required in demo mode.",
            border_style="yellow",
            box=box.ROUNDED,
            expand=False,
        )
    )
    console.print()

    choice = questionary.select(
        "Choose a student scenario:",
        choices=list(_DEMO_SCENARIOS.keys()),
    ).ask()

    if choice is None:
        console.print("[dim]Exited.[/dim]")
        return

    student = _DEMO_SCENARIOS[choice]
    name = student["personal_info"]["first_name"]
    console.print(
        f"\n[dim]Loading profile for [bold]{name} "
        f"{student['personal_info']['last_name']}[/bold]…[/dim]\n"
    )

    run(student)

    console.print()
    if Confirm.ask("[dim]Run another scenario?[/dim]", default=False):
        demo_mode()


# ---------------------------------------------------------------------------
# Standard (login) mode
# ---------------------------------------------------------------------------

def standard_mode() -> None:
    """Full portal login then run."""
    _print_banner()

    student = login_prompt()
    if student is None:
        console.print("[bold red]Authentication failed. Exiting.[/bold red]")
        sys.exit(1)

    run(student)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION}"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode — pick a scenario without logging in.",
    )
    args = parser.parse_args()

    if args.demo:
        demo_mode()
    else:
        standard_mode()


if __name__ == "__main__":
    main()
