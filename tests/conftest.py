import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def prato_valido():
    return {
        "nome": "Prato Teste Fixture",
        "categoria": "massa",
        "preco": 54.0,
        "disponivel": True,
    }