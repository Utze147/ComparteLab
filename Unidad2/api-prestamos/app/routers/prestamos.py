from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PrestamoCreate, PrestamoDevolucion, PrestamoOut
from ..services.prestamos import (
    crear_prestamo_service,
    listar_prestamos_service,
    obtener_prestamo_service,
    registrar_devolucion_service,
)

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])

@router.get("", response_model=list[PrestamoOut])
def listar_prestamos(
    usuario_id: int | None = Query(default=None, ge=1),
    estado: str | None = None,
    db: Session = Depends(get_db)
):
    return listar_prestamos_service(db, usuario_id, estado)

@router.get("/{prestamo_id}", response_model=PrestamoOut)
def obtener_prestamo(
    prestamo_id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    return obtener_prestamo_service(db, prestamo_id)

@router.post("", response_model=PrestamoOut, status_code=status.HTTP_201_CREATED)
def crear_prestamo(datos: PrestamoCreate, db: Session = Depends(get_db)):
    return crear_prestamo_service(db, datos)

@router.patch("/{prestamo_id}", response_model=PrestamoOut)
def registrar_devolucion(
    datos: PrestamoDevolucion,
    prestamo_id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    return registrar_devolucion_service(db, prestamo_id, datos)