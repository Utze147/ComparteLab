from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_crear_prestamo_valido_e_integridad():
    datos = {
        "usuario_id": 1,
        "equipo_id": 1,
        "fecha_esperada_devolucion": "2026-11-15"
    }
    response = client.post("/api/v1/prestamos", json=datos)
    assert response.status_code == 201
    prestamo = response.json()
    assert prestamo["estado"] == "activo"

    # Comprobar integridad: el equipo 1 debe haber cambiado a 'prestado'
    res_equipo = client.get("/api/v1/equipos/1")
    assert res_equipo.status_code == 200
    assert res_equipo.json()["estado"] == "prestado"

def test_prestamo_equipo_ocupado():
    datos = {
        "usuario_id": 2,
        "equipo_id": 1,
        "fecha_esperada_devolucion": "2026-11-16"
    }
    response = client.post("/api/v1/prestamos", json=datos)
    assert response.status_code == 409
    assert response.json()["error"]["codigo"] == "EQUIPO_NO_DISPONIBLE"

def test_prestamo_usuario_inactivo():
    datos = {
        "usuario_id": 3,
        "equipo_id": 2,
        "fecha_esperada_devolucion": "2026-11-16"
    }
    response = client.post("/api/v1/prestamos", json=datos)
    assert response.status_code == 409
    assert response.json()["error"]["codigo"] == "USUARIO_INACTIVO"

def test_devolucion_e_integridad_segunda_devolucion():
    # Primera devolución válida
    res_dev = client.patch("/api/v1/prestamos/1", json={"fecha_devolucion": "2026-10-20"})
    assert res_dev.status_code == 200
    assert res_dev.json()["estado"] == "devuelto"

    # Comprobar que el equipo 1 volvió a 'disponible'
    res_eq = client.get("/api/v1/equipos/1")
    assert res_eq.json()["estado"] == "disponible"

    # Segunda devolución debe ser rechazada con 409
    res_dup = client.patch("/api/v1/prestamos/1", json={"fecha_devolucion": "2026-10-21"})
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["codigo"] == "PRESTAMO_YA_DEVUELTO"