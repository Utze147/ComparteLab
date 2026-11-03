from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_listar_equipos():
    response = client.get("/api/v1/equipos")
    assert response.status_code == 200
    datos = response.json()
    assert isinstance(datos, list)

def test_crear_equipo():
    datos = {
        "tipo": "laptop",
        "marca": "Dell",
        "modelo": "Latitude",
        "numero_inventario": "TEST-PC-001"
    }
    response = client.post("/api/v1/equipos", json=datos)
    assert response.status_code == 201
    resultado = response.json()
    assert resultado["marca"] == "Dell"
    assert resultado["estado"] == "disponible"

def test_equipo_inexistente():
    response = client.get("/api/v1/equipos/999999")
    assert response.status_code == 404
    datos = response.json()
    assert datos["error"]["codigo"] == "EQUIPO_NO_ENCONTRADO"

def test_crear_equipo_invalido():
    datos = {
        "tipo": "automovil",
        "marca": "",
        "modelo": "",
        "numero_inventario": "A"
    }
    response = client.post("/api/v1/equipos", json=datos)
    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == "DATOS_INVALIDOS"

def test_inventario_duplicado():
    datos = {
        "tipo": "laptop",
        "marca": "Lenovo",
        "modelo": "ThinkPad",
        "numero_inventario": "TEST-PC-001"
    }
    response = client.post("/api/v1/equipos", json=datos)
    assert response.status_code == 409
    assert response.json()["error"]["codigo"] == "INVENTARIO_DUPLICADO"