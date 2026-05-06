# tests/test_contratos.py

def test_contrato_get_prato(client):
    """
    Valida se a estrutura de dados de um prato permanece consistente.
    """
    response = client.get("/pratos/1")
    assert response.status_code == 200
    prato = response.json()
    
    # Conjunto de chaves obrigatórias do contrato
    campos = {"id", "nome", "categoria", "preco", "disponivel"}
    assert campos.issubset(prato.keys())
    
    # Validação rigorosa de tipos
    assert isinstance(prato["id"], int)
    assert isinstance(prato["nome"], str)
    assert isinstance(prato["preco"], (int, float))
    assert isinstance(prato["disponivel"], bool)
    assert prato["preco"] > 0

def test_contrato_ml_predict(client):
    """
    Valida o contrato da Inteligência Artificial (Bloco 3 da Checklist).
    """
    payload = {
        "custo_prato": 25.0,
        "dia_da_semana": 5,
        "hora_pedido": 19,
        "tempo_mesa": 60,
        "popularidade": 4.5
    }
    response = client.post("/ml/predict", json=payload)
    assert response.status_code == 200
    dados = response.json()
    
    # Chaves que o modelo DEVE retornar para não quebrar o frontend ou outros serviços
    chaves_esperadas = {"prediction", "probability", "label", "model_version"}
    assert chaves_esperadas.issubset(dados.keys())
    
    # Verificação de tipos para garantir integridade dos dados de ML
    assert isinstance(dados["prediction"], int)
    assert isinstance(dados["probability"], float)
    assert isinstance(dados["label"], str)
    assert "puc-sp-aula" in dados["model_version"]

def test_contrato_post_prato(client):
    """
    Valida a resposta após a criação de um novo recurso.
    """
    novo_prato = {"nome": "Prato Contrato", "categoria": "massa", "preco": 45.0}
    response = client.post("/pratos", json=novo_prato)
    
    assert response.status_code in [200, 201]
    prato = response.json()
    assert "id" in prato
    assert isinstance(prato["id"], int)

def test_contrato_erro_404(client):
    """
    Garante que a estrutura de erro da API seja padronizada.
    """
    response = client.get("/pratos/9999")
    assert response.status_code == 404
    corpo = response.json()
    
    # O erro deve vir com uma mensagem clara em 'detail' ou 'erro'
    mensagem = corpo.get("detail") or corpo.get("erro")
    assert isinstance(mensagem, str) and len(mensagem) > 0