from datetime import date
from typing import Literal

import pymysql
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from database import get_db
from schemas import (
    DevolucionEntrada,
    EquipoEntrada,
    PrestamoEntrada,
    UsuarioEntrada,
)

app = FastAPI(
    title="API de préstamos y resguardos",
    description="Gestión de usuarios, equipos, préstamos y devoluciones.",
    version="1.0.0",
)


@app.exception_handler(pymysql.IntegrityError)
async def error_integridad(request, exc):
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "La operación genera un dato duplicado "
                "o un conflicto con registros relacionados."
            )
        },
    )


@app.exception_handler(pymysql.MySQLError)
async def error_base_datos(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "No se pudo completar la operación de datos."},
    )


@app.get("/", tags=["Inicio"])
def inicio():
    return {
        "mensaje": "API de préstamos y resguardos",
        "documentacion": "/docs",
    }


# ---------------- USUARIOS ----------------

@app.post("/api/usuarios", status_code=201, tags=["Usuarios"])
def crear_usuario(datos: UsuarioEntrada, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, matricula, correo, activo)
            VALUES (%s, %s, %s, %s)
            """,
            (
                datos.nombre,
                datos.matricula,
                datos.correo,
                datos.activo,
            ),
        )
        nuevo_id = cursor.lastrowid

    db.commit()
    return {"id": nuevo_id, **datos.model_dump()}


@app.get("/api/usuarios", tags=["Usuarios"])
def listar_usuarios(
    limite: int = Query(20, ge=1, le=100),
    desplazamiento: int = Query(0, ge=0),
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM usuarios
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (limite, desplazamiento),
        )
        return cursor.fetchall()


@app.get("/api/usuarios/{usuario_id}", tags=["Usuarios"])
def consultar_usuario(usuario_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        usuario = cursor.fetchone()

    if not usuario:
        raise HTTPException(404, "Usuario no encontrado.")

    return usuario


@app.put("/api/usuarios/{usuario_id}", tags=["Usuarios"])
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioEntrada,
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM usuarios WHERE id = %s FOR UPDATE",
            (usuario_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(404, "Usuario no encontrado.")

        cursor.execute(
            """
            UPDATE usuarios
            SET nombre = %s, matricula = %s, correo = %s, activo = %s
            WHERE id = %s
            """,
            (
                datos.nombre,
                datos.matricula,
                datos.correo,
                datos.activo,
                usuario_id,
            ),
        )

    db.commit()
    return {"id": usuario_id, **datos.model_dump()}


@app.delete("/api/usuarios/{usuario_id}", status_code=204, tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "DELETE FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "Usuario no encontrado.")

    db.commit()


# ---------------- EQUIPOS ----------------

@app.post("/api/equipos", status_code=201, tags=["Equipos"])
def crear_equipo(datos: EquipoEntrada, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO equipos (codigo, nombre, descripcion, estado)
            VALUES (%s, %s, %s, %s)
            """,
            (
                datos.codigo,
                datos.nombre,
                datos.descripcion,
                datos.estado,
            ),
        )
        nuevo_id = cursor.lastrowid

    db.commit()
    return {"id": nuevo_id, **datos.model_dump()}


@app.get("/api/equipos", tags=["Equipos"])
def listar_equipos(
    estado: Literal[
        "disponible", "prestado", "mantenimiento", "baja"
    ] | None = None,
    limite: int = Query(20, ge=1, le=100),
    desplazamiento: int = Query(0, ge=0),
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM equipos
            WHERE (%s IS NULL OR estado = %s)
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (estado, estado, limite, desplazamiento),
        )
        return cursor.fetchall()


@app.get("/api/equipos/{equipo_id}", tags=["Equipos"])
def consultar_equipo(equipo_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM equipos WHERE id = %s",
            (equipo_id,),
        )
        equipo = cursor.fetchone()

    if not equipo:
        raise HTTPException(404, "Equipo no encontrado.")

    return equipo


@app.put("/api/equipos/{equipo_id}", tags=["Equipos"])
def actualizar_equipo(
    equipo_id: int,
    datos: EquipoEntrada,
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM equipos WHERE id = %s FOR UPDATE",
            (equipo_id,),
        )
        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(404, "Equipo no encontrado.")

        if equipo["estado"] == "prestado":
            raise HTTPException(
                409,
                "Registra la devolución antes de modificar el equipo.",
            )

        cursor.execute(
            """
            UPDATE equipos
            SET codigo = %s, nombre = %s, descripcion = %s, estado = %s
            WHERE id = %s
            """,
            (
                datos.codigo,
                datos.nombre,
                datos.descripcion,
                datos.estado,
                equipo_id,
            ),
        )

    db.commit()
    return {"id": equipo_id, **datos.model_dump()}


@app.delete("/api/equipos/{equipo_id}", status_code=204, tags=["Equipos"])
def eliminar_equipo(equipo_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "DELETE FROM equipos WHERE id = %s",
            (equipo_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "Equipo no encontrado.")

    db.commit()


# ---------------- PRÉSTAMOS ----------------

@app.post("/api/prestamos", status_code=201, tags=["Préstamos"])
def crear_prestamo(datos: PrestamoEntrada, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM usuarios WHERE id = %s FOR UPDATE",
            (datos.usuario_id,),
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(404, "Usuario no encontrado.")

        if not usuario["activo"]:
            raise HTTPException(409, "El usuario está inactivo.")

        cursor.execute(
            "SELECT * FROM equipos WHERE id = %s FOR UPDATE",
            (datos.equipo_id,),
        )
        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(404, "Equipo no encontrado.")

        if equipo["estado"] != "disponible":
            raise HTTPException(409, "El equipo no está disponible.")

        hoy = date.today()

        cursor.execute(
            """
            INSERT INTO prestamos (
                equipo_id, usuario_id, fecha_prestamo,
                fecha_limite, observaciones
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                datos.equipo_id,
                datos.usuario_id,
                hoy,
                datos.fecha_limite,
                datos.observaciones,
            ),
        )
        nuevo_id = cursor.lastrowid

        cursor.execute(
            "UPDATE equipos SET estado = 'prestado' WHERE id = %s",
            (datos.equipo_id,),
        )

    db.commit()

    return {
        "id": nuevo_id,
        **datos.model_dump(),
        "fecha_prestamo": hoy,
        "estado": "activo",
    }


@app.get("/api/prestamos", tags=["Préstamos"])
def listar_prestamos(
    estado: Literal["activo", "devuelto"] | None = None,
    limite: int = Query(20, ge=1, le=100),
    desplazamiento: int = Query(0, ge=0),
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.*, e.nombre AS equipo, u.nombre AS usuario
            FROM prestamos p
            JOIN equipos e ON e.id = p.equipo_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE (%s IS NULL OR p.estado = %s)
            ORDER BY p.id DESC
            LIMIT %s OFFSET %s
            """,
            (estado, estado, limite, desplazamiento),
        )
        return cursor.fetchall()


@app.get("/api/prestamos/{prestamo_id}", tags=["Préstamos"])
def consultar_prestamo(prestamo_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM prestamos WHERE id = %s",
            (prestamo_id,),
        )
        prestamo = cursor.fetchone()

    if not prestamo:
        raise HTTPException(404, "Préstamo no encontrado.")

    return prestamo


# ---------------- DEVOLUCIONES ----------------

@app.post("/api/devoluciones", status_code=201, tags=["Devoluciones"])
def crear_devolucion(datos: DevolucionEntrada, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM prestamos WHERE id = %s FOR UPDATE",
            (datos.prestamo_id,),
        )
        prestamo = cursor.fetchone()

        if not prestamo:
            raise HTTPException(404, "Préstamo no encontrado.")

        if prestamo["estado"] != "activo":
            raise HTTPException(409, "El préstamo ya fue devuelto.")

        hoy = date.today()

        cursor.execute(
            """
            INSERT INTO devoluciones (
                prestamo_id, fecha_devolucion, condicion, observaciones
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                datos.prestamo_id,
                hoy,
                datos.condicion,
                datos.observaciones,
            ),
        )
        nuevo_id = cursor.lastrowid

        cursor.execute(
            "UPDATE prestamos SET estado = 'devuelto' WHERE id = %s",
            (datos.prestamo_id,),
        )

        nuevo_estado = (
            "disponible" if datos.condicion == "bueno"
            else "mantenimiento"
        )

        cursor.execute(
            "UPDATE equipos SET estado = %s WHERE id = %s",
            (nuevo_estado, prestamo["equipo_id"]),
        )

    db.commit()

    return {
        "id": nuevo_id,
        **datos.model_dump(),
        "fecha_devolucion": hoy,
        "estado_equipo": nuevo_estado,
    }


@app.get("/api/devoluciones", tags=["Devoluciones"])
def listar_devoluciones(
    limite: int = Query(20, ge=1, le=100),
    desplazamiento: int = Query(0, ge=0),
    db=Depends(get_db),
):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM devoluciones
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (limite, desplazamiento),
        )
        return cursor.fetchall()


@app.get("/api/devoluciones/{devolucion_id}", tags=["Devoluciones"])
def consultar_devolucion(devolucion_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM devoluciones WHERE id = %s",
            (devolucion_id,),
        )
        devolucion = cursor.fetchone()

    if not devolucion:
        raise HTTPException(404, "Devolución no encontrada.")

    return devolucion