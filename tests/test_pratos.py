import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.smoke
def test_raiz_retorna_nome_restaurante():
    response = client.get("/")
    assert response.status_code == 200
    assert "Bella Tavola" in response.json()["restaurante"]


@pytest.mark.smoke
def test_listar_pratos_retorna_200():
    response = client.get("/pratos")
    assert response.status_code == 200


@pytest.mark.smoke
def test_listar_pratos_retorna_lista_nao_vazia():
    response = client.get("/pratos")
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_filtro_por_categoria_retorna_apenas_categoria_correta():
    response = client.get("/pratos?categoria=pizza")
    assert response.status_code == 200
    for prato in response.json():
        assert prato["categoria"] == "pizza"


def test_buscar_prato_existente_retorna_campos_esperados():
    response = client.get("/pratos/1")
    assert response.status_code == 200
    prato = response.json()
    assert "id" in prato
    assert "nome" in prato
    assert "preco" in prato


@pytest.mark.smoke
def test_buscar_prato_inexistente_retorna_404():
    response = client.get("/pratos/9999")
    assert response.status_code == 404


@pytest.mark.validacao
def test_criar_prato_valido():
    response = client.post("/pratos", json={
        "nome": "Funghi Trifolati Teste",
        "categoria": "massa",
        "preco": 54.0,
        "disponivel": True,
    })
    assert response.status_code in [200, 201]
    dados = response.json()
    assert dados["nome"] == "Funghi Trifolati Teste"
    assert "id" in dados


@pytest.mark.validacao
def test_criar_prato_preco_negativo_retorna_422():
    response = client.post("/pratos", json={"nome": "Prato", "categoria": "pizza", "preco": -10.0})
    assert response.status_code == 422


@pytest.mark.validacao
def test_criar_prato_nome_curto_retorna_422():
    response = client.post("/pratos", json={"nome": "AB", "categoria": "pizza", "preco": 40.0})
    assert response.status_code == 422


@pytest.mark.validacao
def test_criar_prato_categoria_invalida_retorna_422():
    response = client.post("/pratos", json={"nome": "Prato Exótico", "categoria": "japonesa", "preco": 40.0})
    assert response.status_code == 422


def test_prato_criado_aparece_na_listagem():
    nome_unico = "Tagliatelle Exclusivo XYZ-9871"
    client.post("/pratos", json={"nome": nome_unico, "categoria": "massa", "preco": 68.0})
    response = client.get("/pratos")
    nomes = [p["nome"] for p in response.json()]
    assert nome_unico in nomes


@pytest.mark.parametrize("categoria_invalida", [
    "esoterico", "fastfood", "japonesa", "PIZZA", "massa extra",
])
def test_categoria_invalida_retorna_422(categoria_invalida):
    response = client.post("/pratos", json={"nome": "Prato Teste", "categoria": categoria_invalida, "preco": 40.0})
    assert response.status_code == 422


@pytest.mark.parametrize("id_inexistente", [9999, 123456])
def test_prato_inexistente_retorna_404(id_inexistente):
    response = client.get(f"/pratos/{id_inexistente}")
    assert response.status_code == 404