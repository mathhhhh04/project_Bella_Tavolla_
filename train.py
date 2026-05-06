import os
import numpy as np
import pandas as pd
import sklearn
import joblib as jl
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from huggingface_hub import HfApi, login
from typing import Tuple

def gerar_dataset_bella_tavola(
    n_samples: int = 2000,
    seed: int = 42,
    proporcao_positivos: float = 0.25
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    [BLOCO 1] - Função Geradora do Domínio Bella Tavola.
    Gera dados sintéticos de pedidos de alto risco para o restaurante.
    Target 1 indica um pedido potencialmente problemático/fraude.
    """
    if not (0.05 <= proporcao_positivos <= 0.95):
        raise ValueError("proporcao_positivos deve estar entre 0.05 e 0.95")

    rng = np.random.default_rng(seed)
    risco = rng.choice(
        [0, 1],
        size=n_samples,
        p=[1 - proporcao_positivos, proporcao_positivos]
    )

    # Regra de negócio do restaurante para gerar o padrão de risco
    valor_pedido = np.where(risco, rng.uniform(250, 900, n_samples), rng.uniform(25, 180, n_samples)).round(2)
    hora_pedido = np.where(risco, rng.choice([0, 1, 2, 3, 23], n_samples), rng.integers(11, 22, n_samples))
    num_itens = np.where(risco, rng.integers(6, 14, n_samples), rng.integers(1, 4, n_samples))
    historico_cancelamentos = np.where(risco, rng.integers(2, 5, n_samples), rng.integers(0, 1, n_samples))
    distancia_entrega = np.where(risco, rng.uniform(12, 45, n_samples), rng.uniform(0.5, 7, n_samples)).round(1)

    df = pd.DataFrame({
        "valor_pedido": valor_pedido,
        "hora_pedido": hora_pedido,
        "num_itens": num_itens,
        "historico_cancelamentos": historico_cancelamentos,
        "distancia_entrega": distancia_entrega,
        "target": risco
    })

    X = df.drop(columns=["target"]).values
    y = df["target"].values
    return df, X, y

if __name__ == "__main__":
    print("🤖 [BLOCO 1] Gerando dados sintéticos coerentes para o Bella Tavola...")
    df, X, y = gerar_dataset_bella_tavola(n_samples=2000, seed=42)
    
    print("\n📊 [BLOCO 2] Treinando o RandomForestClassifier...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["legitimo", "risco"])
    print("\nMétricas de Validação do Modelo:\n", report)
    
    # Serialização do artefato local
    jl.dump(model, "model.pkl")
    print("✅ Artefato 'model.pkl' gerado com sucesso localmente.")

    print("\n🤗 [BLOCO 3] Autenticando e publicando no Hugging Face Hub...")
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("❌ Erro: A variável de ambiente 'HF_TOKEN' não foi configurada no terminal.")
        exit(1)
        
    login(token=token)
    api = HfApi()
    username = api.whoami()["name"]
    repo_id = f"{username}/mlops-bella-tavola-v1"
    
    print(f"📦 Vinculando ao Registry: {repo_id}")
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
    
    # Gerando o arquivo de dependências do modelo (requirements.txt)
    with open("requirements.txt", "w") as f:
        f.write(f"scikit-learn=={sklearn.__version__}\njoblib=={jl.__version__}\nnumpy=={np.__version__}\n")
        
    # Construindo o Model Card (README.md do repositório de ML)
    model_card_content = f"""---
language: pt
tags:
  - sklearn
  - classification
  - restaurante
  - mlops
---
# Bella Tavola - Classificador de Risco de Pedidos 🍝

Modelo preditivo desenvolvido para analisar o risco logístico e financeiro de pedidos no restaurante Bella Tavola.

## Contrato de Features (Ordem Rigorosa)
1. valor_pedido (float) - Valor em Reais
2. hora_pedido (int) - Intervalo de 0 a 23
3. num_itens (int) - Volumetria de pratos no carrinho
4. historico_cancelamentos (int) - Cancelamentos anteriores do cliente
5. distancia_entrega (float) - Raio de entrega em km

## Desempenho do Modelo

{report}
"""

    with open("README_model.md", "w", encoding="utf-8") as f:
        f.write(model_card_content)

    print("📤 Enviando arquivos para o Hugging Face...")
    api.upload_file(path_or_fileobj="model.pkl", path_in_repo="model.pkl", repo_id=repo_id, repo_type="model", commit_message="feat: upload model artifact")
    api.upload_file(path_or_fileobj="requirements.txt", path_in_repo="requirements.txt", repo_id=repo_id, repo_type="model", commit_message="chore: add requirements")
    api.upload_file(path_or_fileobj="README_model.md", path_in_repo="README.md", repo_id=repo_id, repo_type="model", commit_message="docs: create model card")

    if os.path.exists("README_model.md"):
        os.remove("README_model.md")
        
    print(f"\n🚀 Sucesso! Repositório publicado em: [https://huggingface.co/](https://huggingface.co/){repo_id}")