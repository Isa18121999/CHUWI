from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notificacion
from app.websocket_manager import ws_manager


async def crear_notificacion(
    db: AsyncSession,
    tipo: str,
    mensaje: str,
    sesion_id: int | None = None,
):
    notif = Notificacion(
        sesion_id=sesion_id,
        tipo=tipo,
        mensaje=mensaje,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    await ws_manager.broadcast("notificacion", {
        "id": notif.id,
        "tipo": notif.tipo,
        "mensaje": notif.mensaje,
        "sesion_id": notif.sesion_id,
        "timestamp": notif.timestamp.isoformat(),
    })

    return notif
