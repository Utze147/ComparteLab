from __future__ import annotations
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    prestamos: Mapped[list["Prestamo"]] = relationship(
        back_populates="usuario"
    )

class Equipo(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30))
    marca: Mapped[str] = mapped_column(String(50))
    modelo: Mapped[str] = mapped_column(String(80))
    numero_inventario: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    estado: Mapped[str] = mapped_column(String(20), default="disponible")

    prestamos: Mapped[list["Prestamo"]] = relationship(
        back_populates="equipo"
    )

class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"))
    fecha_prestamo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    fecha_esperada_devolucion: Mapped[date] = mapped_column(Date)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo")

    usuario: Mapped["Usuario"] = relationship(back_populates="prestamos")
    equipo: Mapped["Equipo"] = relationship(back_populates="prestamos")