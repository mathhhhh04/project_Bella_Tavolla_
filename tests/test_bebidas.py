import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.smoke
def test_listar_bebidas_retorna_200():
    response = client.get("/bebidas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filtro_por_tipo():
    response = client.get("/bebidas?tipo=vinho")
    assert response.status_code == 200
    for b in response.json():
        assert b["tipo"] == "vinho"


def test_filtro_por_alcoolica():
    response = client.get("/bebidas?alcoolica=false")
    assert response.status_code == 200
    for b in response.json():
        assert b["alcoolica"] == False


def test_buscar_bebida_existente():
    response = client.get("/bebidas/1")
    assert response.status_code == 200
    assert "nome" in response.json()


def test_buscar_bebida_inexistente_retorna_404():
    response = client.get("/bebidas/9999")
    assert response.status_code == 404


@pytest.mark.validacao
def test_criar_bebida_valida():
    response = client.post("/bebidas", json={
        "nome": "Água Tônica Teste",
        "tipo": "agua",
        "preco": 9.0,
        "alcoolica": False,
        "volume_ml": 350,
    })
    assert response.status_code in [200, 201]