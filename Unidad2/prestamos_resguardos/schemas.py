from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModeloBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class UsuarioEntrada(ModeloBase):
    nombre: str = Field(min_length=3, max_length=100)
    matricula: str = Field(min_length=3, max_length=30)
    correo: str = Field(
        max_length=150,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    activo: bool = True


class EquipoEntrada(ModeloBase):
    codigo: str = Field(min_length=2, max_length=30)
    nombre: str = Field(min_length=3, max_length=100)
    descripcion: str = Field(default="", max_length=500)
    estado: Literal["disponible", "mantenimiento", "baja"] = "disponible"


class PrestamoEntrada(ModeloBase):
    equipo_id: int = Field(gt=0)
    usuario_id: int = Field(gt=0)
    fecha_limite: date
    observaciones: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validar_fecha(self):
        if self.fecha_limite < date.today():
            raise ValueError(
                "La fecha límite no puede ser anterior a hoy."
            )
        return self


class DevolucionEntrada(ModeloBase):
    prestamo_id: int = Field(gt=0)
    condicion: Literal["bueno", "danado"]
    observaciones: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validar_observaciones(self):
        if self.condicion == "danado" and not self.observaciones:
            raise ValueError(
                "Describe el daño en las observaciones."
            )
        return self