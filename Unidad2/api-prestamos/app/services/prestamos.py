from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..errors import AppError
from ..models import Equipo, Prestamo, Usuario
from ..schemas import PrestamoCreate, PrestamoDevolucion

def listar_prestamos_service(
    db: Session,
    usuario_id: int | None = None,
    estado: str | None = None
) -> list[Prestamo]:
    consulta = select(Prestamo)
    if usuario_id is not None:
        consulta = consulta.where(Prestamo.usuario_id == usuario_id)
    if estado is not None:
        consulta = consulta.where(Prestamo.estado == estado)
    return list(db.scalars(consulta).all())

def obtener_prestamo_service(db: Session, prestamo_id: int) -> Prestamo:
    prestamo = db.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise AppError(
            404,
            "PRESTAMO_NO_ENCONTRADO",
            "El préstamo solicitado no existe."
        )
    return prestamo

def crear_prestamo_service(db: Session, datos: PrestamoCreate) -> Prestamo:
    # 1. ¿Existe el usuario?
    usuario = db.get(Usuario, datos.usuario_id)
    if usuario is None:
        raise AppError(
            404,
            "USUARIO_NO_ENCONTRADO",
            "El usuario solicitado no existe."
        )

    # 2. ¿Está activo el usuario?
    if not usuario.activo:
        raise AppError(
            409,
            "USUARIO_INACTIVO",
            "El usuario no puede realizar préstamos."
        )

    # 3. ¿Tiene menos de 2 préstamos activos?
    cantidad = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.usuario_id == datos.usuario_id,
            Prestamo.estado == "activo"
        )
    )
    if cantidad is not None and cantidad >= 2:
        raise AppError(
            409,
            "LIMITE_PRESTAMOS",
            "El usuario ya tiene dos préstamos activos."
        )

    # 4. ¿Existe el equipo?
    equipo = db.get(Equipo, datos.equipo_id)
    if equipo is None:
        raise AppError(
            404,
            "EQUIPO_NO_ENCONTRADO",
            "El equipo solicitado no existe."
        )

    # 5. ¿Está disponible el equipo?
    if equipo.estado != "disponible":
        raise AppError(
            409,
            "EQUIPO_NO_DISPONIBLE",
            "El equipo solicitado no está disponible."
        )

    # 6. Transacción atómica: INSERT préstamo + UPDATE estado del equipo
    prestamo = Prestamo(
        usuario_id=usuario.id,
        equipo_id=equipo.id,
        fecha_esperada_devolucion=datos.fecha_esperada_devolucion,
        estado="activo"
    )
    try:
        db.add(prestamo)
        equipo.estado = "prestado"
        db.commit()
        db.refresh(prestamo)
        return prestamo
    except Exception:
        db.rollback()
        raise

def registrar_devolucion_service(
    db: Session, prestamo_id: int, datos: PrestamoDevolucion
) -> Prestamo:
    prestamo = obtener_prestamo_service(db, prestamo_id)

    if prestamo.estado == "devuelto":
        raise AppError(
            409,
            "PRESTAMO_YA_DEVUELTO",
            "El préstamo ya fue devuelto."
        )

    try:
        prestamo.fecha_devolucion = datos.fecha_devolucion
        prestamo.estado = "devuelto"
        prestamo.equipo.estado = "disponible"
        db.commit()
        db.refresh(prestamo)
        return prestamo
    except Exception:
        db.rollback()
        raise