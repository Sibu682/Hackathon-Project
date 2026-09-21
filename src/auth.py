"""
Authentication module — simulates student portal login.

Validates credentials against the simulation dataset and returns
the authenticated student record on success.
"""

import bcrypt
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

from data import STUDENT_DATABASE

console = Console()


# ---------------------------------------------------------------------------
# Core authentication logic
# ---------------------------------------------------------------------------

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def authenticate(username: str, password: str) -> Optional[dict]:
    """
    Attempt to authenticate a student by username and password.

    Returns:
        The student record dict if credentials are valid, else None.
    """
    student = STUDENT_DATABASE.get(username.strip().lower())
    if student is None:
        return None

    if _verify_password(password, student["password_hash"]):
        return student

    return None


# ---------------------------------------------------------------------------
# Interactive login prompt (CLI)
# ---------------------------------------------------------------------------

MAX_ATTEMPTS: int = 3


def login_prompt() -> Optional[dict]:
    """
    Display the UNISA portal login screen and prompt the user for credentials.

    Allows up to MAX_ATTEMPTS before locking out.

    Returns:
        Authenticated student record, or None if authentication fails.
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]UNISA Student Portal[/bold cyan]\n"
            "[dim]AI-Powered Financial Aid Assistant[/dim]",
            box=box.DOUBLE,
            expand=False,
            border_style="cyan",
        )
    )
    console.print()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        console.print(f"[dim]Login attempt {attempt} of {MAX_ATTEMPTS}[/dim]")

        username = Prompt.ask("[bold]Student username[/bold]")
        password = Prompt.ask("[bold]Password[/bold]", password=True)

        student = authenticate(username, password)

        if student:
            _print_login_success(student)
            return student

        remaining = MAX_ATTEMPTS - attempt
        if remaining > 0:
            console.print(
                f"[red]✗ Incorrect username or password. "
                f"{remaining} attempt(s) remaining.[/red]\n"
            )
        else:
            console.print(
                "[bold red]✗ Too many failed attempts. "
                "Your session has been locked.[/bold red]\n"
            )
            console.print(
                "[dim]If you have forgotten your password, please visit "
                "https://my.unisa.ac.za or contact the UNISA helpdesk.[/dim]"
            )

    return None


def _print_login_success(student: dict) -> None:
    """Print a welcome banner after successful login."""
    name = student["personal_info"]["first_name"]
    student_id = student["student_id"]

    console.print()
    console.print(
        Panel(
            f"[bold green]✓ Login successful[/bold green]\n\n"
            f"Welcome, [bold]{name}[/bold]  ·  Student No: [bold]{student_id}[/bold]",
            box=box.ROUNDED,
            border_style="green",
            expand=False,
        )
    )
    console.print()
