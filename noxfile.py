"""Автоматические действия с кодом."""

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"

# Fast check
# ==========


@nox.session(python=["3.12"], tags=["cur"])
def ruff_lint_cur(session: nox.Session) -> None:
    """Проверяет качество кода при помощи Ruff."""
    session.install("ruff")
    session.run("ruff", "check")


@nox.session(python=["3.12"], tags=["cur"])
def type_check_cur(session: nox.Session) -> None:
    """Проверка статической типизации при помощи mypy."""
    session.run("uv", "sync", "--active")
    session.run("mypy", "-p", "maubot")


# Full check
# ==========


@nox.session(python=["3.11", "3.12", "3.13"], tags=["full"])
def ruff_lint(session: nox.Session) -> None:
    """Проверяет качество кода при помощи Ruff."""
    session.install("ruff")
    session.run("ruff", "check")


@nox.session(python=["3.11", "3.12", "3.13"], tags=["full"])
def type_check(session: nox.Session) -> None:
    """Проверка статической типизации при помощи mypy."""
    session.run("uv", "sync", "--active")
    session.run("mypy", "-p", "maubot")
