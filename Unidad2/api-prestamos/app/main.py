from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .errors import AppError
from .models import Base
from .routers import equipos, prestamos

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Préstamo de Equipos",
    version="1.0.0"
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    contenido = {
        "error": {
            "codigo": exc.codigo,
            "mensaje": exc.mensaje
        }
    }
    if exc.detalles is not None:
        contenido["error"]["detalles"] = exc.detalles
    return JSONResponse(status_code=exc.status_code, content=contenido)

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "codigo": "DATOS_INVALIDOS",
                "mensaje": "La solicitud contiene datos inválidos.",
                "detalles": exc.errors()
            }
        }
    )

app.include_router(equipos.router, prefix="/api/v1")
app.include_router(prestamos.router, prefix="/api/v1")