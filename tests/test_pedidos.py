import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.smoke
def test_criar_pedido_valido():
    response = client.post("/pedidos", json={"prato_id": 1, "quantidade": 2})
    assert response.status_code in [200, 201]
    dados = response.json()
    assert dados["prato_id"] == 1
    assert dados["quantidade"] == 2
    assert dados["valor_total"] > 0


def test_criar_pedido_prato_inexistente_retorna_404():
    response = client.post("/pedidos", json={"prato_id": 9999, "quantidade": 1})
    assert response.status_code == 404


def test_criar_pedido_prato_indisponivel_retorna_400():
    # prato_id=3 (Lasanha Bolonhesa) está com disponivel=False nos dados iniciais
    response = client.post("/pedidos", json={"prato_id": 3, "quantidade": 1})
    assert response.status_code == 400


def test_listar_pedidos_retorna_lista():
    response = client.get("/pedidos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)