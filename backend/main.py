from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS para permitir que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista temporal para guardar las solicitudes
solicitudes = []


class Solicitud(BaseModel):
    matricula: str
    nombre_alumno: str
    equipo_id: int
    motivo: str


@app.post("/api/v1/solicitudes", status_code=201)
def crear_solicitud(solicitud: Solicitud):

    nueva_solicitud = {
        "id": len(solicitudes) + 1,
        "matricula": solicitud.matricula,
        "nombre_alumno": solicitud.nombre_alumno,
        "equipo_id": solicitud.equipo_id,
        "motivo": solicitud.motivo,
        "estado": "PENDIENTE"
    }

    solicitudes.append(nueva_solicitud)

    return nueva_solicitud


@app.get("/api/v1/solicitudes")
def obtener_solicitudes():
    return solicitudes