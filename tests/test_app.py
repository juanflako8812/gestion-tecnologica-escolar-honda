from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def build_client(tmp_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setenv("GTE_DB_PATH", str(tmp_path / "test.sqlite3"))
    import app.database as database

    importlib.reload(database)
    database.init_db(seed=True)

    import app.main as main

    importlib.reload(main)
    return TestClient(main.app)


def login(client: TestClient, username: str = "admin", password: str = "admin123") -> None:
    response = client.post("/login", data={"username": username, "password": password}, follow_redirects=False)
    assert response.status_code == 303


def test_health_check(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_and_dashboard(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    login(client)
    response = client.get("/")
    assert response.status_code == 200
    assert "Panel de control" in response.text
    assert "Activos registrados" in response.text


def test_asset_creation_and_list(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    login(client)
    response = client.post(
        "/activos/nuevo",
        data={
            "code": "TEST-CPU-100",
            "name": "Equipo de prueba",
            "category": "Computador",
            "brand": "Dell",
            "model": "OptiPlex",
            "serial": "SERIAL-100",
            "location": "Laboratorio de pruebas",
            "status": "Disponible",
            "responsible": "Soporte",
            "notes": "Activo creado por prueba automatizada",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = client.get("/activos?q=TEST-CPU-100")
    assert response.status_code == 200
    assert "TEST-CPU-100" in response.text


def test_ticket_creation_and_close(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    login(client)
    response = client.post(
        "/tickets/nuevo",
        data={
            "title": "Falla en equipo de prueba",
            "description": "El equipo presenta intermitencia durante el encendido.",
            "priority": "Alta",
            "asset_id": 1,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    ticket_url = response.headers["location"]
    ticket_id = ticket_url.rstrip("/").split("/")[-1]
    response = client.post(
        f"/tickets/{ticket_id}/actualizar",
        data={"status": "Cerrado", "assigned_to_id": 2, "resolution": "Se verificó fuente de poder y se cerró el caso."},
        follow_redirects=False,
    )
    assert response.status_code == 303
    response = client.get(ticket_url)
    assert response.status_code == 200
    assert "Cerrado" in response.text
    assert "Se verificó fuente de poder" in response.text


def test_reports_page(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    login(client)
    response = client.get("/reportes")
    assert response.status_code == 200
    assert "Reportes operativos" in response.text
    assert "Estado de activos" in response.text


def test_export_assets_csv(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    login(client)
    response = client.get("/export/activos.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "code,name,category" in response.text
