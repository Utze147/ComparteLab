from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import EquipoCreate, EquipoOut, EquipoUpdate
from ..services.equipos import (
    actualizar_equipo_service,
    crear_equipo_service,
    eliminar_equipo_service,
    listar_equipos_service,
    obtener_equipo_service,
)

router = APIRouter(prefix="/equipos", tags=["Equipos"])

@router.get("", response_model=list[EquipoOut])
def listar_equipos(
    estado: str | None = None,
    tipo: str | None = None,
    buscar: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return listar_equipos_service(db, estado, tipo, buscar, limit, offset)

@router.get("/{equipo_id}", response_model=EquipoOut)
def obtener_equipo(
    equipo_id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    return obtener_equipo_service(db, equipo_id)

@router.post("", response_model=EquipoOut, status_code=status.HTTP_201_CREATED)
def crear_equipo(datos: EquipoCreate, db: Session = Depends(get_db)):
    return crear_equipo_service(db, datos)

@router.patch("/{equipo_id}", response_model=EquipoOut)
def actualizar_equipo(
    datos: EquipoUpdate,
    equipo_id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    return actualizar_equipo_service(db, equipo_id, datos)

@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_equipo(
    equipo_id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    eliminar_equipo_service(db, equipo_id)