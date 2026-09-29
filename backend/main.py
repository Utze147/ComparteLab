from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==============================================================================
# 1. BASE DE DATOS Y PERSISTENCIA (SQLite)
# ==============================================================================
DB_PATH = Path(__file__).parent / "comparte_lab.db"

def obtener_conexion():
    """Abre conexión con SQLite y configura row_factory para trabajar con diccionarios."""
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion

def crear_base_datos():
    """Crea la tabla de solicitudes si no existe al iniciar la aplicación."""
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS solicitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                nombre_alumno TEXT NOT NULL,
                equipo_id INTEGER NOT NULL,
                motivo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'PENDIENTE'
            )
            """
        )

# ==============================================================================
# 2. MODELO DE ENTRADA Y VALIDACIÓN (Pydantic)
# ==============================================================================
class SolicitudEntrada(BaseModel):
    matricula: str = Field(min_length=3, max_length=20, description="Matrícula del estudiante")
    nombre_alumno: str = Field(min_length=3, max_length=100, description="Nombre completo")
    equipo_id: int = Field(gt=0, description="Identificador del equipo (entero positivo)")
    motivo: str = Field(min_length=5, max_length=300, description="Motivo del préstamo")

class ActualizarEstadoEntrada(BaseModel):
    estado: str = Field(description="Nuevo estado: APROBADA, RECHAZADA o DEVUELTO")

# ==============================================================================
# 3. INICIALIZACIÓN Y CONFIGURACIÓN DE FASTAPI
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_base_datos()
    yield

app = FastAPI(
    title="ComparteLab API - Sistema de Préstamo de Laboratorio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS: Permite la comunicación entre el frontend y el backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# 4. ENDPOINT POST: REGISTRAR SOLICITUD
# ==============================================================================
@app.post("/api/v1/solicitudes", status_code=201)
def crear_solicitud(solicitud: SolicitudEntrada):
    """
    Registra una nueva solicitud de préstamo.
    - 201: Creado con éxito.
    - 409: Conflicto de negocio (el equipo ya está solicitado o en uso).
    - 422: Datos inválidos (manejado por Pydantic).
    """
    matricula = solicitud.matricula.strip().upper()
    nombre_alumno = solicitud.nombre_alumno.strip()
    equipo_id = solicitud.equipo_id
    motivo = solicitud.motivo.strip()

    with obtener_conexion() as conexion:
        # REGLA DE NEGOCIO: No permitir préstamo de un equipo ya ocupado o en espera
        conflicto = conexion.execute(
            """
            SELECT id, matricula, nombre_alumno, estado
            FROM solicitudes
            WHERE equipo_id = ?
              AND estado IN ('PENDIENTE', 'APROBADA')
            LIMIT 1
            """,
            (equipo_id,)
        ).fetchone()

        if conflicto:
            raise HTTPException(
                status_code=409,
                detail=f"El equipo #{equipo_id} ya se encuentra solicitado o en uso por {conflicto['nombre_alumno']} ({conflicto['estado']})."
            )

        # PERSISTENCIA EN SQLITE
        cursor = conexion.execute(
            """
            INSERT INTO solicitudes (matricula, nombre_alumno, equipo_id, motivo, estado)
            VALUES (?, ?, ?, ?, 'PENDIENTE')
            """,
            (matricula, nombre_alumno, equipo_id, motivo)
        )
        nueva_id = cursor.lastrowid

        nueva_solicitud = conexion.execute(
            "SELECT * FROM solicitudes WHERE id = ?",
            (nueva_id,)
        ).fetchone()

        return dict(nueva_solicitud)

# ==============================================================================
# 5. ENDPOINT GET: LISTAR SOLICITUDES
# ==============================================================================
@app.get("/api/v1/solicitudes")
def obtener_solicitudes():
    """Retorna todas las solicitudes registradas ordenadas de la más reciente a la más antigua."""
    with obtener_conexion() as conexion:
        filas = conexion.execute(
            "SELECT * FROM solicitudes ORDER BY id DESC"
        ).fetchall()
        return [dict(fila) for fila in filas]

# ==============================================================================
# 6. ENDPOINT PATCH: CAMBIAR ESTADO (Aprobar, Rechazar o Marcar Devuelto)
# ==============================================================================
@app.patch("/api/v1/solicitudes/{id}/estado")
def actualizar_estado(id: int, entrada: ActualizarEstadoEntrada):
    """
    Permite al laboratorista o docente gestionar la solicitud:
    Aprobar, Rechazar o Devolver el equipo para liberarlo.
    """
    nuevo_estado = entrada.estado.strip().upper()
    estados_validos = ["APROBADA", "RECHAZADA", "DEVUELTO", "PENDIENTE"]

    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Opciones válidas: {', '.join(estados_validos)}"
        )

    with obtener_conexion() as conexion:
        actual = conexion.execute(
            "SELECT * FROM solicitudes WHERE id = ?", (id,)
        ).fetchone()

        if not actual:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada.")

        conexion.execute(
            "UPDATE solicitudes SET estado = ? WHERE id = ?",
            (nuevo_estado, id)
        )

        actualizada = conexion.execute(
            "SELECT * FROM solicitudes WHERE id = ?", (id,)
        ).fetchone()

        return dict(actualizada)