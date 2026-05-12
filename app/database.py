from __future__ import annotations

import csv
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.sqlite3"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_db_path() -> Path:
    return Path(os.getenv("GTE_DB_PATH", str(DEFAULT_DB_PATH))).resolve()


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, digest_hex = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return hmac.compare_digest(candidate, digest_hex)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(query, tuple(params)).fetchone()
    return row_to_dict(row)


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def execute(query: str, params: Iterable[Any] = ()) -> int:
    with get_connection() as conn:
        cursor = conn.execute(query, tuple(params))
        conn.commit()
        return int(cursor.lastrowid)


def execute_script(script: str) -> None:
    with get_connection() as conn:
        conn.executescript(script)
        conn.commit()


def init_db(seed: bool = True) -> None:
    execute_script(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL CHECK(role IN ('admin', 'soporte', 'usuario')),
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            serial TEXT,
            location TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Disponible', 'Asignado', 'En mantenimiento', 'Retirado')),
            responsible TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Baja', 'Media', 'Alta', 'Crítica')),
            status TEXT NOT NULL CHECK(status IN ('Abierto', 'Asignado', 'En proceso', 'Cerrado')),
            asset_id INTEGER,
            requester_id INTEGER NOT NULL,
            assigned_to_id INTEGER,
            resolution TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT,
            FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE SET NULL,
            FOREIGN KEY(requester_id) REFERENCES users(id) ON DELETE RESTRICT,
            FOREIGN KEY(assigned_to_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            ticket_id INTEGER,
            maintenance_type TEXT NOT NULL CHECK(maintenance_type IN ('Preventivo', 'Correctivo')),
            description TEXT NOT NULL,
            performed_by TEXT NOT NULL,
            result TEXT NOT NULL,
            cost REAL NOT NULL DEFAULT 0,
            maintenance_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            entity TEXT NOT NULL,
            entity_id INTEGER,
            detail TEXT,
            created_at TEXT NOT NULL
        );
        """
    )
    if seed:
        seed_demo_data()


def create_user(username: str, password: str, full_name: str, role: str, email: str = "") -> int:
    return execute(
        """
        INSERT INTO users(username, password_hash, full_name, email, role, active, created_at)
        VALUES(?, ?, ?, ?, ?, 1, ?)
        """,
        (username, hash_password(password), full_name, email, role, utc_now()),
    )


def get_user_by_username(username: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM users WHERE username = ? AND active = 1", (username,))


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def record_audit(actor: str, action: str, entity: str, entity_id: int | None = None, detail: str = "") -> None:
    execute(
        """
        INSERT INTO audit_logs(actor, action, entity, entity_id, detail, created_at)
        VALUES(?, ?, ?, ?, ?, ?)
        """,
        (actor, action, entity, entity_id, detail, utc_now()),
    )


def seed_demo_data() -> None:
    user_count = fetch_one("SELECT COUNT(*) AS total FROM users")
    if user_count and user_count["total"] == 0:
        create_user("admin", "admin123", "Administrador del sistema", "admin", "admin@example.edu.co")
        create_user("soporte", "soporte123", "Responsable de soporte", "soporte", "soporte@example.edu.co")
        create_user("docente", "docente123", "Usuario solicitante", "usuario", "docente@example.edu.co")

    asset_count = fetch_one("SELECT COUNT(*) AS total FROM assets")
    if asset_count and asset_count["total"] == 0:
        now = utc_now()
        assets = [
            ("LAB-CPU-001", "Equipo laboratorio 1", "Computador", "Lenovo", "ThinkCentre", "SN-LAB001", "Sala de informática", "Disponible", "Coordinación TIC", "Equipo de demostración TRL5"),
            ("LAB-CPU-002", "Equipo laboratorio 2", "Computador", "HP", "ProDesk", "SN-LAB002", "Sala de informática", "Asignado", "Docente de tecnología", "Registro inicial del piloto"),
            ("ADM-IMP-001", "Impresora administrativa", "Impresora", "Epson", "L3250", "SN-IMP001", "Secretaría", "En mantenimiento", "Secretaría académica", "Falla intermitente en impresión"),
        ]
        with get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO assets(code, name, category, brand, model, serial, location, status, responsible, notes, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [(*asset, now, now) for asset in assets],
            )
            conn.commit()

    ticket_count = fetch_one("SELECT COUNT(*) AS total FROM tickets")
    if ticket_count and ticket_count["total"] == 0:
        docente = get_user_by_username("docente")
        soporte = get_user_by_username("soporte")
        asset = fetch_one("SELECT id FROM assets WHERE code = ?", ("ADM-IMP-001",))
        if docente and soporte and asset:
            now = utc_now()
            execute(
                """
                INSERT INTO tickets(title, description, priority, status, asset_id, requester_id, assigned_to_id, resolution, created_at, updated_at, closed_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Impresora no imprime desde equipo administrativo",
                    "La impresora recibe la orden, pero el documento queda en cola y no se imprime.",
                    "Alta",
                    "En proceso",
                    asset["id"],
                    docente["id"],
                    soporte["id"],
                    "",
                    now,
                    now,
                    None,
                ),
            )


def get_dashboard_metrics() -> dict[str, Any]:
    metrics = {}
    metrics["assets_total"] = fetch_one("SELECT COUNT(*) AS total FROM assets")["total"]
    metrics["tickets_open"] = fetch_one("SELECT COUNT(*) AS total FROM tickets WHERE status <> 'Cerrado'")["total"]
    metrics["tickets_closed"] = fetch_one("SELECT COUNT(*) AS total FROM tickets WHERE status = 'Cerrado'")["total"]
    metrics["maintenance_total"] = fetch_one("SELECT COUNT(*) AS total FROM maintenance")["total"]
    avg = fetch_one(
        """
        SELECT AVG((julianday(closed_at) - julianday(created_at)) * 24.0) AS hours
        FROM tickets
        WHERE closed_at IS NOT NULL
        """
    )
    metrics["average_resolution_hours"] = round(avg["hours"] or 0, 2)
    metrics["assets_by_status"] = fetch_all("SELECT status, COUNT(*) AS total FROM assets GROUP BY status ORDER BY status")
    metrics["tickets_by_priority"] = fetch_all("SELECT priority, COUNT(*) AS total FROM tickets GROUP BY priority ORDER BY priority")
    return metrics


def export_csv(query: str, headers: list[str], params: Iterable[Any] = ()) -> str:
    rows = fetch_all(query, params)
    output_path = get_db_path().parent / f"export_{secrets.token_hex(4)}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return str(output_path)
