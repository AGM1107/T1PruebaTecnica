import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import db


@pytest.fixture(scope="module")
def client():
    """
    Fixture que crea un cliente de prueba para la API y limpia la base de datos después de que todas las pruebas del módulo se ejecuten.
    """
    with TestClient(app) as test_client:
        yield test_client

    print("\n--- Limpiando base de datos de prueba ---")
    db["clientes"].delete_many({})
    db["tarjetas"].delete_many({})
    db["cobros"].delete_many({})


def test_read_root(client):
    """Prueba que el endpoint raíz '/' funcione."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a la API de Cobros Simulados"}


test_data = {}


def test_01_full_workflow_crud_clientes(client):
    """
    Prueba el flujo completo del CRUD de Clientes
    """
    cliente_payload = {
        "nombre": "Cliente de Prueba",
        "email": "test@example.com",
        "telefono": "5512345678"
    }
    response = client.post("/clientes", json=cliente_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == cliente_payload["nombre"]
    assert "_id" in data

    test_data["cliente_id"] = data["_id"]

    response = client.get(f"/clientes/{test_data['cliente_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == cliente_payload["email"]

    update_payload = {"nombre": "Cliente Actualizado"}
    response = client.put(f"/clientes/{test_data['cliente_id']}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Cliente Actualizado"


def test_02_full_workflow_crud_tarjetas(client):
    """
    Prueba el flujo completo del CRUD de Tarjetas
    """
    tarjeta_luhn_fail = {
        "cliente_id": test_data["cliente_id"],
        "pan_completo": "4111111111111112"
    }
    response = client.post("/tarjetas", json=tarjeta_luhn_fail)
    assert response.status_code == 400
    assert "no es válido" in response.json()["detail"]

    tarjeta_aprobar = {
        "cliente_id": test_data["cliente_id"],
        "pan_completo": "4111111111111111"
    }
    response = client.post("/tarjetas", json=tarjeta_aprobar)
    assert response.status_code == 201
    data = response.json()
    assert data["last4"] == "1111"
    assert data["pan_masked"] == "************1111"
    test_data["tarjeta_aprobar_id"] = data["_id"]

    tarjeta_rechazar = {
        "cliente_id": test_data["cliente_id"],
        "pan_completo": "4000000000002222"
    }
    response = client.post("/tarjetas", json=tarjeta_rechazar)
    assert response.status_code == 201
    data = response.json()
    assert data["last4"] == "2222"
    test_data["tarjeta_rechazar_id"] = data["_id"]

    response = client.get(f"/tarjetas/{test_data['tarjeta_aprobar_id']}")
    assert response.status_code == 200
    assert response.json()["last4"] == "1111"


def test_03_full_workflow_cobros_y_reembolsos(client):
    """
    Prueba el flujo de Cobros  y Reembolsos
    """
    cobro_aprobado = {
        "tarjeta_id": test_data["tarjeta_aprobar_id"],
        "cliente_id": test_data["cliente_id"],
        "monto": 100.0
    }
    response = client.post("/cobros", json=cobro_aprobado)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "approved"
    assert data["codigo_motivo"] == "00"
    test_data["cobro_aprobado_id"] = data["_id"]

    cobro_rechazado = {
        "tarjeta_id": test_data["tarjeta_rechazar_id"],
        "cliente_id": test_data["cliente_id"],
        "monto": 200.0
    }
    response = client.post("/cobros", json=cobro_rechazado)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "declined"
    assert data["codigo_motivo"] == "51"

    response = client.post(f"/cobros/{test_data['cobro_aprobado_id']}/reembolso")
    assert response.status_code == 200
    data = response.json()
    assert data["reembolsado"] == True
    assert data["fecha_reembolso"] is not None

    response = client.post(f"/cobros/{test_data['cobro_aprobado_id']}/reembolso")
    assert response.status_code == 400
    assert "ya ha sido reembolsado" in response.json()["detail"]


def test_04_full_workflow_historial_y_delete(client):
    """
    Prueba la consulta de historial  y la limpieza (DELETE) [cite: 43, 44]
    """
    response = client.get(f"/cobros/{test_data['cliente_id']}")
    assert response.status_code == 200
    historial = response.json()

    assert len(historial) == 2

    cobro_reembolsado = next(c for c in historial if c["_id"] == test_data["cobro_aprobado_id"])
    assert cobro_reembolsado["reembolsado"] == True
    assert cobro_reembolsado["status"] == "approved"

    cobro_declinado = next(c for c in historial if c["_id"] != test_data["cobro_aprobado_id"])
    assert cobro_declinado["reembolsado"] == False
    assert cobro_declinado["status"] == "declined"

    response = client.delete(f"/tarjetas/{test_data['tarjeta_aprobar_id']}")
    assert response.status_code == 204
    response = client.delete(f"/tarjetas/{test_data['tarjeta_rechazar_id']}")
    assert response.status_code == 204

    response = client.delete(f"/clientes/{test_data['cliente_id']}")
    assert response.status_code == 204

    response = client.get(f"/clientes/{test_data['cliente_id']}")
    assert response.status_code == 404
