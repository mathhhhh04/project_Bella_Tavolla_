# tests/test_saude.py
import pytest

@pytest.mark.smoke
def test_health_check_endpoint_status(client):
    """
    Valida se o endpoint de saúde responde com o status code 200 (Bloco 3).
    """
    response = client.get("/ml/health")
    assert response.status_code == 200

def test_health_check_response_structure(client):
    """
    Verifica se a estrutura do JSON contém as chaves obrigatórias definidas no contrato (Bloco 3).
    """
    response = client.get("/ml/health")
    dados = response.json()
    
    assert "status" in dados
    assert "model" in dados
    assert dados["status"] == "ok"
    # O estado do modelo deve ser reportado de forma consistente com a lógica de resiliência
    assert dados["model"] in ["ok", "degraded"]

def test_health_check_relative_behavior(client):
    """
    Valida comportamentos relativos: a resposta varia conforme o estado do carregamento do modelo (Bloco 4).
    """
    response = client.get("/ml/health")
    dados = response.json()
    
    if dados["model"] == "ok":
        # Valida se o identificador do repositório está correto no estado operacional
        assert "repo" in dados
        assert "puc-sp-aula" in dados["repo"]
    elif dados["model"] == "degraded":
        # Valida se o detalhe do erro é exposto quando o modelo falha
        assert "detail" in dados