from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .auth import can_manage_assets, can_manage_tickets, get_current_user, role_label
from .database import (
    authenticate,
    execute,
    export_csv,
    fetch_all,
    fetch_one,
    get_dashboard_metrics,
    init_db,
    record_audit,
    utc_now,
)

BASE_DIR = Path(__file__).resolve().parent
@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db(seed=True)
    yield


app = FastAPI(title="Gestión tecnológica escolar", version="1.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="prototipo-trl5-cambiar-en-produccion")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals["role_label"] = role_label


def render(request: Request, template: str, context: dict[str, Any] | None = None) -> Response:
    user = get_current_user(request)
    ctx: dict[str, Any] = {"request": request, "user": user}
    if context:
        ctx.update(context)
    return templates.TemplateResponse(request, template, ctx)


def redirect_to_login() -> Response:
    return RedirectResponse(url="/login", status_code=303)


def require_user(request: Request) -> dict[str, Any] | RedirectResponse:
    user = get_current_user(request)
    if not user:
        return redirect_to_login()
    return user


def forbidden(request: Request, message: str = "El usuario no tiene permisos para ejecutar esta acción.") -> Response:
    return render(request, "error.html", {"message": message})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request) -> Response:
    if get_current_user(request):
        return RedirectResponse(url="/", status_code=303)
    return render(request, "login.html", {"error": ""})


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)) -> Response:
    user = authenticate(username.strip(), password)
    if not user:
        return render(request, "login.html", {"error": "Usuario o contraseña inválidos."})
    request.session["username"] = user["username"]
    record_audit(user["username"], "Inicio de sesión", "users", user["id"], "Acceso al prototipo")
    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
def logout(request: Request) -> Response:
    user = get_current_user(request)
    if user:
        record_audit(user["username"], "Cierre de sesión", "users", user["id"], "Salida del prototipo")
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    metrics = get_dashboard_metrics()
    latest_tickets = fetch_all(
        """
        SELECT t.*, a.code AS asset_code, u.full_name AS requester_name
        FROM tickets t
        LEFT JOIN assets a ON a.id = t.asset_id
        INNER JOIN users u ON u.id = t.requester_id
        ORDER BY t.created_at DESC
        LIMIT 5
        """
    )
    return render(request, "dashboard.html", {"metrics": metrics, "latest_tickets": latest_tickets})


@app.get("/activos", response_class=HTMLResponse)
def asset_list(request: Request, status: str = "", q: str = "") -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    query = "SELECT * FROM assets WHERE 1=1"
    params: list[Any] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if q:
        query += " AND (code LIKE ? OR name LIKE ? OR location LIKE ? OR responsible LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like, like])
    query += " ORDER BY updated_at DESC"
    assets = fetch_all(query, params)
    return render(request, "assets/list.html", {"assets": assets, "status": status, "q": q, "can_manage": can_manage_assets(user)})


@app.get("/activos/nuevo", response_class=HTMLResponse)
def asset_new_form(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    return render(request, "assets/form.html", {"asset": None, "action": "/activos/nuevo"})


@app.post("/activos/nuevo")
def asset_create(
    request: Request,
    code: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(""),
    model: str = Form(""),
    serial: str = Form(""),
    location: str = Form(...),
    status: str = Form(...),
    responsible: str = Form(""),
    notes: str = Form(""),
) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    now = utc_now()
    asset_id = execute(
        """
        INSERT INTO assets(code, name, category, brand, model, serial, location, status, responsible, notes, created_at, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (code.strip(), name.strip(), category.strip(), brand.strip(), model.strip(), serial.strip(), location.strip(), status, responsible.strip(), notes.strip(), now, now),
    )
    record_audit(user["username"], "Creación de activo", "assets", asset_id, code.strip())
    return RedirectResponse(url="/activos", status_code=303)


@app.get("/activos/{asset_id}", response_class=HTMLResponse)
def asset_detail(request: Request, asset_id: int) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    asset = fetch_one("SELECT * FROM assets WHERE id = ?", (asset_id,))
    if not asset:
        return forbidden(request, "El activo solicitado no existe.")
    tickets = fetch_all("SELECT * FROM tickets WHERE asset_id = ? ORDER BY created_at DESC", (asset_id,))
    maintenance = fetch_all("SELECT * FROM maintenance WHERE asset_id = ? ORDER BY maintenance_date DESC", (asset_id,))
    return render(request, "assets/detail.html", {"asset": asset, "tickets": tickets, "maintenance": maintenance, "can_manage": can_manage_assets(user)})


@app.get("/activos/{asset_id}/editar", response_class=HTMLResponse)
def asset_edit_form(request: Request, asset_id: int) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    asset = fetch_one("SELECT * FROM assets WHERE id = ?", (asset_id,))
    if not asset:
        return forbidden(request, "El activo solicitado no existe.")
    return render(request, "assets/form.html", {"asset": asset, "action": f"/activos/{asset_id}/editar"})


@app.post("/activos/{asset_id}/editar")
def asset_update(
    request: Request,
    asset_id: int,
    code: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(""),
    model: str = Form(""),
    serial: str = Form(""),
    location: str = Form(...),
    status: str = Form(...),
    responsible: str = Form(""),
    notes: str = Form(""),
) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    execute(
        """
        UPDATE assets
        SET code = ?, name = ?, category = ?, brand = ?, model = ?, serial = ?, location = ?, status = ?, responsible = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (code.strip(), name.strip(), category.strip(), brand.strip(), model.strip(), serial.strip(), location.strip(), status, responsible.strip(), notes.strip(), utc_now(), asset_id),
    )
    record_audit(user["username"], "Actualización de activo", "assets", asset_id, code.strip())
    return RedirectResponse(url=f"/activos/{asset_id}", status_code=303)


@app.get("/tickets", response_class=HTMLResponse)
def ticket_list(request: Request, status: str = "", priority: str = "") -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    query = """
        SELECT t.*, a.code AS asset_code, u.full_name AS requester_name, s.full_name AS assigned_name
        FROM tickets t
        LEFT JOIN assets a ON a.id = t.asset_id
        INNER JOIN users u ON u.id = t.requester_id
        LEFT JOIN users s ON s.id = t.assigned_to_id
        WHERE 1=1
    """
    params: list[Any] = []
    if status:
        query += " AND t.status = ?"
        params.append(status)
    if priority:
        query += " AND t.priority = ?"
        params.append(priority)
    query += " ORDER BY t.created_at DESC"
    tickets = fetch_all(query, params)
    return render(request, "tickets/list.html", {"tickets": tickets, "status": status, "priority": priority, "can_manage": can_manage_tickets(user)})


@app.get("/tickets/nuevo", response_class=HTMLResponse)
def ticket_new_form(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    assets = fetch_all("SELECT id, code, name FROM assets ORDER BY code")
    return render(request, "tickets/form.html", {"ticket": None, "assets": assets, "users": [], "action": "/tickets/nuevo", "can_manage": can_manage_tickets(user)})


@app.post("/tickets/nuevo")
def ticket_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    asset_id: int = Form(0),
) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    now = utc_now()
    ticket_id = execute(
        """
        INSERT INTO tickets(title, description, priority, status, asset_id, requester_id, assigned_to_id, resolution, created_at, updated_at, closed_at)
        VALUES(?, ?, ?, 'Abierto', ?, ?, NULL, '', ?, ?, NULL)
        """,
        (title.strip(), description.strip(), priority, asset_id if asset_id else None, user["id"], now, now),
    )
    record_audit(user["username"], "Creación de ticket", "tickets", ticket_id, title.strip())
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)


@app.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_detail(request: Request, ticket_id: int) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    ticket = fetch_one(
        """
        SELECT t.*, a.code AS asset_code, a.name AS asset_name, u.full_name AS requester_name, s.full_name AS assigned_name
        FROM tickets t
        LEFT JOIN assets a ON a.id = t.asset_id
        INNER JOIN users u ON u.id = t.requester_id
        LEFT JOIN users s ON s.id = t.assigned_to_id
        WHERE t.id = ?
        """,
        (ticket_id,),
    )
    if not ticket:
        return forbidden(request, "El ticket solicitado no existe.")
    users = fetch_all("SELECT id, full_name FROM users WHERE role IN ('admin', 'soporte') AND active = 1 ORDER BY full_name")
    maintenance = fetch_all("SELECT * FROM maintenance WHERE ticket_id = ? ORDER BY created_at DESC", (ticket_id,))
    return render(request, "tickets/detail.html", {"ticket": ticket, "users": users, "maintenance": maintenance, "can_manage": can_manage_tickets(user)})


@app.post("/tickets/{ticket_id}/actualizar")
def ticket_update(
    request: Request,
    ticket_id: int,
    status: str = Form(...),
    assigned_to_id: int = Form(0),
    resolution: str = Form(""),
) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_tickets(user):
        return forbidden(request)
    closed_at = utc_now() if status == "Cerrado" else None
    execute(
        """
        UPDATE tickets
        SET status = ?, assigned_to_id = ?, resolution = ?, updated_at = ?, closed_at = COALESCE(?, closed_at)
        WHERE id = ?
        """,
        (status, assigned_to_id if assigned_to_id else None, resolution.strip(), utc_now(), closed_at, ticket_id),
    )
    record_audit(user["username"], "Actualización de ticket", "tickets", ticket_id, status)
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)


@app.get("/mantenimientos", response_class=HTMLResponse)
def maintenance_list(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    rows = fetch_all(
        """
        SELECT m.*, a.code AS asset_code, a.name AS asset_name
        FROM maintenance m
        INNER JOIN assets a ON a.id = m.asset_id
        ORDER BY m.maintenance_date DESC, m.created_at DESC
        """
    )
    return render(request, "maintenance/list.html", {"rows": rows, "can_manage": can_manage_assets(user)})


@app.get("/mantenimientos/nuevo", response_class=HTMLResponse)
def maintenance_new_form(request: Request, ticket_id: int = 0) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    assets = fetch_all("SELECT id, code, name FROM assets ORDER BY code")
    tickets = fetch_all("SELECT id, title FROM tickets WHERE status <> 'Cerrado' ORDER BY created_at DESC")
    return render(request, "maintenance/form.html", {"assets": assets, "tickets": tickets, "ticket_id": ticket_id})


@app.post("/mantenimientos/nuevo")
def maintenance_create(
    request: Request,
    asset_id: int = Form(...),
    ticket_id: int = Form(0),
    maintenance_type: str = Form(...),
    description: str = Form(...),
    performed_by: str = Form(...),
    result: str = Form(...),
    cost: float = Form(0),
    maintenance_date: str = Form(...),
) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if not can_manage_assets(user):
        return forbidden(request)
    maintenance_id = execute(
        """
        INSERT INTO maintenance(asset_id, ticket_id, maintenance_type, description, performed_by, result, cost, maintenance_date, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (asset_id, ticket_id if ticket_id else None, maintenance_type, description.strip(), performed_by.strip(), result.strip(), cost, maintenance_date, utc_now()),
    )
    new_status = "En mantenimiento" if maintenance_type == "Correctivo" and "pendiente" in result.lower() else "Disponible"
    execute("UPDATE assets SET status = ?, updated_at = ? WHERE id = ?", (new_status, utc_now(), asset_id))
    record_audit(user["username"], "Registro de mantenimiento", "maintenance", maintenance_id, maintenance_type)
    return RedirectResponse(url="/mantenimientos", status_code=303)


@app.get("/reportes", response_class=HTMLResponse)
def reports(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    metrics = get_dashboard_metrics()
    recent_audit = fetch_all("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 20")
    return render(request, "reports.html", {"metrics": metrics, "audit": recent_audit})


@app.get("/export/activos.csv")
def export_assets(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    csv_path = export_csv(
        "SELECT code, name, category, brand, model, serial, location, status, responsible, updated_at FROM assets ORDER BY code",
        ["code", "name", "category", "brand", "model", "serial", "location", "status", "responsible", "updated_at"],
    )
    return FileResponse(csv_path, media_type="text/csv", filename="activos.csv")


@app.get("/export/tickets.csv")
def export_tickets(request: Request) -> Response:
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    csv_path = export_csv(
        """
        SELECT t.id, t.title, t.priority, t.status, a.code AS asset_code, t.created_at, t.closed_at
        FROM tickets t
        LEFT JOIN assets a ON a.id = t.asset_id
        ORDER BY t.created_at DESC
        """,
        ["id", "title", "priority", "status", "asset_code", "created_at", "closed_at"],
    )
    return FileResponse(csv_path, media_type="text/csv", filename="tickets.csv")
