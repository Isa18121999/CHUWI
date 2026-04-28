from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db, init_db
from app.models import Interaccion, Notificacion, SesionRobot, Usuario
from app.robot_controller import robot
from app.websocket_manager import ws_manager

app = FastAPI(title="Chuwibot", version="1.0.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---- Startup ----

@app.on_event("startup")
async def on_startup():
    await init_db()
    # Create default admin if not exists
    from app.database import async_session
    async with async_session() as db:
        result = await db.execute(select(Usuario).where(Usuario.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = Usuario(
                username="admin",
                password_hash=hash_password("admin123"),
                rol="admin",
            )
            db.add(admin)
            await db.commit()


# ---- Auth API ----

class RegisterRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "rol": user.rol}


@app.post("/api/register")
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede registrar usuarios")
    existing = await db.execute(select(Usuario).where(Usuario.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    user = Usuario(username=req.username, password_hash=hash_password(req.password))
    db.add(user)
    await db.commit()
    return {"message": "Usuario creado"}


# ---- Robot Control API ----

@app.post("/api/robot/start")
async def robot_start(current_user: Usuario = Depends(get_current_user)):
    if robot.is_running:
        raise HTTPException(status_code=400, detail="Robot ya está activo")
    await robot.start()
    return {"message": "Robot iniciado", "state": robot.state.value}


@app.post("/api/robot/stop")
async def robot_stop(current_user: Usuario = Depends(get_current_user)):
    if not robot.is_running:
        raise HTTPException(status_code=400, detail="Robot ya está detenido")
    await robot.stop()
    return {"message": "Robot detenido", "state": robot.state.value}


@app.get("/api/robot/status")
async def robot_status():
    return {
        "state": robot.state.value,
        "session_id": robot.current_session_id,
    }


# ---- Dashboard API ----

@app.get("/api/sessions")
async def get_sessions(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(SesionRobot).order_by(desc(SesionRobot.inicio)).limit(limit)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "inicio": s.inicio.isoformat(),
            "fin": s.fin.isoformat() if s.fin else None,
            "emocion_inicial": s.emocion_inicial,
        }
        for s in sessions
    ]


@app.get("/api/sessions/{session_id}/interactions")
async def get_interactions(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaccion)
        .where(Interaccion.sesion_id == session_id)
        .order_by(Interaccion.timestamp)
    )
    interactions = result.scalars().all()
    return [
        {
            "id": i.id,
            "rol": i.rol,
            "texto": i.texto,
            "emocion": i.emocion,
            "timestamp": i.timestamp.isoformat(),
        }
        for i in interactions
    ]


@app.get("/api/notifications")
async def get_notifications(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Notificacion).order_by(desc(Notificacion.timestamp)).limit(limit)
    )
    notifs = result.scalars().all()
    return [
        {
            "id": n.id,
            "tipo": n.tipo,
            "mensaje": n.mensaje,
            "timestamp": n.timestamp.isoformat(),
            "leida": n.leida,
            "sesion_id": n.sesion_id,
        }
        for n in notifs
    ]


@app.post("/api/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Notificacion).where(Notificacion.id == notif_id))
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notif.leida = True
    await db.commit()
    return {"message": "Marcada como leída"}


@app.get("/api/dashboard/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    total_sessions = await db.scalar(select(func.count(SesionRobot.id)))
    total_interactions = await db.scalar(select(func.count(Interaccion.id)))
    unread_notifs = await db.scalar(
        select(func.count(Notificacion.id)).where(Notificacion.leida == False)
    )

    # Emotions breakdown
    emotions_result = await db.execute(
        select(SesionRobot.emocion_inicial, func.count(SesionRobot.id))
        .where(SesionRobot.emocion_inicial.isnot(None))
        .group_by(SesionRobot.emocion_inicial)
    )
    emotions = {row[0]: row[1] for row in emotions_result.all()}

    return {
        "total_sessions": total_sessions or 0,
        "total_interactions": total_interactions or 0,
        "unread_notifications": unread_notifs or 0,
        "emotions": emotions,
        "robot_state": robot.state.value,
    }


# ---- WebSocket ----

@app.websocket("/ws/robot")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ---- Pages (Jinja2) ----

@app.get("/", response_class=HTMLResponse)
async def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def page_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})
