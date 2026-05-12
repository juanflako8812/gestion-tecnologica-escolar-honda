from __future__ import annotations

from typing import Any

from fastapi import Request

from .database import get_user_by_username


ROLE_LABELS = {
    "admin": "Administrador",
    "soporte": "Soporte",
    "usuario": "Usuario solicitante",
}


def get_current_user(request: Request) -> dict[str, Any] | None:
    username = request.session.get("username")
    if not username:
        return None
    return get_user_by_username(username)


def can_manage_assets(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") in {"admin", "soporte"})


def can_manage_tickets(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") in {"admin", "soporte"})


def role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role)
