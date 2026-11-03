from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class EquipoCreate(BaseModel):
    tipo: Literal["laptop", "proyector"]
    marca: str = Field(min_length=2, max_length=50)
    modelo: str = Field(min_length=1, max_length=80)
    numero_inventario: str = Field(min_length=3, max_length=50)

class EquipoUpdate(BaseModel):
    tipo: Literal["laptop", "proyector"] | None = None
    marca: str | None = Field(default=None, min_length=2, max_length=50)
    modelo: str | None = Field(default=None, min_length=1, max_length=80)
    estado: Literal["disponible", "prestado", "mantenimiento"] | None = None

class EquipoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    marca: str
    modelo: str
    numero_inventario: str
    estado: str

class PrestamoCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    equipo_id: int = Field(gt=0)
    fecha_esperada_devolucion: date

    @field_validator("fecha_esperada_devolucion")
    @classmethod
    def validar_fecha(cls, valor: date) -> date:
        if valor <= date.today():
            raise ValueError("La fecha de devolución debe ser futura.")
        return valor

class PrestamoDevolucion(BaseModel):
    fecha_devolucion: date

class PrestamoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    equipo_id: int
    fecha_prestamo: datetime
    fecha_esperada_devolucion: date
    fecha_devolucion: date | None
    estado: str