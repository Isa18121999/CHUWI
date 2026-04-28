import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), default="operador")
    creado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SesionRobot(Base):
    __tablename__ = "sesiones_robot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inicio: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fin: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    emocion_inicial: Mapped[str | None] = mapped_column(String(50), nullable=True)

    interacciones: Mapped[list["Interaccion"]] = relationship(back_populates="sesion")
    notificaciones: Mapped[list["Notificacion"]] = relationship(back_populates="sesion")


class Interaccion(Base):
    __tablename__ = "interacciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesiones_robot.id"))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rol: Mapped[str] = mapped_column(String(20))  # "usuario" | "robot"
    texto: Mapped[str] = mapped_column(Text)
    emocion: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sesion: Mapped["SesionRobot"] = relationship(back_populates="interacciones")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sesion_id: Mapped[int | None] = mapped_column(
        ForeignKey("sesiones_robot.id"), nullable=True
    )
    tipo: Mapped[str] = mapped_column(String(30))  # "hablar" | "activacion" | "error"
    mensaje: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    leida: Mapped[bool] = mapped_column(Boolean, default=False)

    sesion: Mapped["SesionRobot | None"] = relationship(back_populates="notificaciones")
