from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..errors import AppError
from ..models import Equipo
from ..schemas import EquipoCreate, EquipoUpdate

def listar_equipos_service(
    db: Session,
    estado: str | None = None,
    tipo: str | None = None,
    buscar: str | None = None,
    limit: int = 20,
    offset: int = 0
) -> list[Equipo]:
    consulta = select(Equipo)

    if estado is not None:
        consulta = consulta.where(Equipo.estado == estado)
    if tipo is not None:
        consulta = consulta.where(Equipo.tipo == tipo)
    if buscar:
        patron = f"%{buscar}%"
        consulta = consulta.where(Equipo.marca.ilike(patron))

    consulta = consulta.offset(offset).limit(limit)
    return list(db.scalars(consulta).all())

def obtener_equipo_service(db: Session, equipo_id: int) -> Equipo:
    equipo = db.get(Equipo, equipo_id)
    if equipo is None:
        raise AppError(
            404,
            "EQUIPO_NO_ENCONTRADO",
            "El equipo solicitado no existe."
        )
    return equipo

def crear_equipo_service(db: Session, datos: EquipoCreate) -> Equipo:
    existente = db.scalar(
        select(Equipo).where(Equipo.numero_inventario == datos.numero_inventario)
    )
    if existente is not None:
        raise AppError(
            409,
            "INVENTARIO_DUPLICADO",
            "Ya existe un equipo con ese número de inventario."
        )

    equipo = Equipo(
        tipo=datos.tipo,
        marca=datos.marca,
        modelo=datos.modelo,
        numero_inventario=datos.numero_inventario,
        estado="disponible"
    )
    try:
        db.add(equipo)
        db.commit()
        db.refresh(equipo)
        return equipo
    except IntegrityError:
        db.rollback()
        raise AppError(
            409,
            "INVENTARIO_DUPLICADO",
            "Ya existe un equipo con ese número de inventario."
        )

def actualizar_equipo_service(
    db: Session, equipo_id: int, datos: EquipoUpdate
) -> Equipo:
    equipo = obtener_equipo_service(db, equipo_id)
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return equipo

def eliminar_equipo_service(db: Session, equipo_id: int) -> None:
    equipo = obtener_equipo_service(db, equipo_id)
    if equipo.estado == "prestado":
        raise AppError(
            409,
            "EQUIPO_CON_PRESTAMO",
            "No se puede eliminar un equipo prestado."
        )
    db.delete(equipo)
    db.commit()