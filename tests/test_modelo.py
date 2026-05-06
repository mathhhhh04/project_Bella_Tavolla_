import pytest
import numpy as np
from model_utils import load_model

# Configuração do repositório oficial definido no projeto
REPO_ID = "joaogabriel101735/puc-sp-aula"

@pytest.fixture(scope="module")
def modelo():
    """
    Carrega o modelo uma única vez para todos os testes do módulo (Otimização CI).
    Utiliza a função load_model que consome o HF_TOKEN do ambiente.
    """
    return load_model(REPO_ID)

@pytest.fixture
def payload_valido():
    """
    Retorna um payload de exemplo alinhado com o schema do PredictInput.
    """
    return {
        "custo_prato": 25.50,
        "dia_da_semana": 5, # Sexta-feira
        "hora_pedido": 20,  # Horário de pico
        "tempo_mesa": 45,
        "popularidade": 4.8
    }

# --- TESTES DE INTEGRAÇÃO DO OBJETO (Bloco 5.2) ---

@pytest.mark.integracao
def test_modelo_carregado_com_sucesso(modelo):
    """Verifica se o artefato .pkl foi carregado e não está vazio."""
    assert modelo is not None
    assert hasattr(modelo, "predict"), "O modelo deve ter o método predict"
    assert hasattr(modelo, "predict_proba"), "O modelo deve ter o método predict_proba"

@pytest.mark.integracao
def test_modelo_inferencia_basica(modelo):
    """Verifica se o modelo aceita um array numpy e retorna o formato correto."""
    amostra = np.array([[30.0, 0, 12, 30, 4.0]])
    predicao = modelo.predict(amostra)
    probabilidade = modelo.predict_proba(amostra)
    
    assert len(predicao) == 1
    assert probabilidade.shape == (1, 2), "O modelo deve retornar probabilidades para 2 classes"

# --- TESTES DO ENDPOINT DA API (Bloco 5.3) ---

@pytest.mark.integracao
def test_api_predict_sucesso(client, payload_valido):
    """Valida o contrato e a resposta do endpoint /ml/predict."""
    response = client.post("/ml/predict", json=payload_valido)
    assert response.status_code == 200
    
    dados = response.json()
    assert "prediction" in dados
    assert "probability" in dados
    assert "model_version" in dados
    assert dados["prediction"] in [0, 1]
    assert 0 <= dados["probability"] <= 1

@pytest.mark.integracao
@pytest.mark.parametrize("campo,valor_errado", [
    ("dia_da_semana", 10), # Fora do range 0-6
    ("hora_pedido", -1),   # Fora do range 0-23
    ("popularidade", 6.0), # Fora do range 1-5
    ("custo_prato", -5.0)  # Valor negativo inválido
])
def test_api_predict_validacao_campos(client, payload_valido, campo, valor_errado):
    """Garante que a API rejeita dados fora das regras do Pydantic."""
    payload_errado = payload_valido.copy()
    payload_errado[campo] = valor_errado
    
    response = client.post("/ml/predict", json=payload_errado)
    assert response.status_code == 422

# --- TESTES DE COMPORTAMENTO E SANIDADE (Bloco 5.5) ---

@pytest.mark.integracao
def test_modelo_sanidade_distincao_casos(client):
    """
    Verifica se o modelo distingue casos extremos (Alta vs Baixa demanda).
    """
    caso_baixa = {"custo_prato": 10.0, "dia_da_semana": 1, "hora_pedido": 15, "tempo_mesa": 20, "popularidade": 2.0}
    caso_alta = {"custo_prato": 80.0, "dia_da_semana": 5, "hora_pedido": 20, "tempo_mesa": 90, "popularidade": 5.0}

    res_baixa = client.post("/ml/predict", json=caso_baixa).json()["probability"]
    res_alta = client.post("/ml/predict", json=caso_alta).json()["probability"]

    # Em um modelo saudável, as probabilidades devem ser distintas para contextos opostos
    assert res_alta != res_baixa, "O modelo deve reagir a mudanças drásticas de contexto"

@pytest.mark.integracao
def test_modelo_deterministico(client, payload_valido):
    """Garante que o mesmo input gera sempre o mesmo output."""
    res1 = client.post("/ml/predict", json=payload_valido).json()
    res2 = client.post("/ml/predict", json=payload_valido).json()
    
    assert res1["probability"] == res2["probability"]
    assert res1["prediction"] == res2["prediction"]