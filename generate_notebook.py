import json

notebook_content = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": "title_cell",
            "metadata": {},
            "source": [
                "# Do dado sintético ao modelo em produção — Bella Tavola 🍝\n",
                "## MLOps Pipeline — Semana 2"
            ]
        },
        {
            "cell_type": "markdown",
            "id": "intro_cell",
            "metadata": {},
            "source": [
                "Este caderno documenta o ciclo completo de gerenciamento do ciclo de vida de Machine Learning para a plataforma **Bella Tavola**:\n",
                "1. Geração de dados sintéticos alinhados à regra de negócio do restaurante.\n",
                "2. Treinamento de um `RandomForestClassifier` para mitigação de risco operacional em pedidos.\n",
                "3. Publicação e versionamento do artefato binário no **Hugging Face Hub** (Model Registry).\n",
                "4. Validação da inferência com cache local e garantia do contrato de dados."
            ]
        },
        {
            "cell_type": "markdown",
            "id": "block1_title",
            "metadata": {},
            "source": [
                "--- \n",
                "# BLOCO 1 — Dados Sintéticos com Sabor de Restaurante 🍕"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "block1_code",
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "import pandas as pd\n",
                "from typing import Tuple\n",
                "\n",
                "def gerar_dataset_bella_tavola(\n",
                "    n_samples: int = 2000,\n",
                "    seed: int = 42,\n",
                "    proporcao_positivos: float = 0.25\n",
                ") -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:\n",
                "    \"\"\"\n",
                "    Gera dataset sintético de pedidos de alto risco para o Bella Tavola.\n",
                "    Target 1 indica um pedido potencialmente problemático/fraude.\n",
                "    \"\"\"\n",
                "    if not (0.05 <= proporcao_positivos <= 0.95):\n",
                "        raise ValueError(\"proporcao_positivos deve estar entre 0.05 e 0.95\")\n",
                "\n",
                "    rng = np.random.default_rng(seed)\n",
                "    risco = rng.choice(\n",
                "        [0, 1],\n",
                "        size=n_samples,\n",
                "        p=[1 - proporcao_positivos, proporcao_positivos]\n",
                "    )\n",
                "\n",
                "    # Simulação das regras de negócio do domínio\n",
                "    valor_pedido = np.where(risco, rng.uniform(250, 900, n_samples), rng.uniform(25, 180, n_samples)).round(2)\n",
                "    hora_pedido = np.where(risco, rng.choice([0, 1, 2, 3, 23], n_samples), rng.integers(11, 22, n_samples))\n",
                "    num_itens = np.where(risco, rng.integers(6, 14, n_samples), rng.integers(1, 4, n_samples))\n",
                "    historico_cancelamentos = np.where(risco, rng.integers(2, 5, n_samples), rng.integers(0, 1, n_samples))\n",
                "    distancia_entrega = np.where(risco, rng.uniform(12, 45, n_samples), rng.uniform(0.5, 7, n_samples)).round(1)\n",
                "\n",
                "    df = pd.DataFrame({\n",
                "        \"valor_pedido\": valor_pedido,\n",
                "        \"hora_pedido\": hora_pedido,\n",
                "        \"num_itens\": num_itens,\n",
                "        \"historico_cancelamentos\": historico_cancelamentos,\n",
                "        \"distancia_entrega\": distancia_entrega,\n",
                "        \"target\": risco\n",
                "    })\n",
                "\n",
                "    X = df.drop(columns=[\"target\"]).values\n",
                "    y = df[\"target\"].values\n",
                "    return df, X, y\n",
                "\n",
                "df, X, y = gerar_dataset_bella_tavola(n_samples=2000, seed=42)\n",
                "print(\"✅ Dataset gerado!\")\n",
                "print(df.groupby(\"target\").mean().round(2))"
            ]
        },
        {
            "cell_type": "markdown",
            "id": "block2_title",
            "metadata": {},
            "source": [
                "--- \n",
                "# BLOCO 2 — Treinamento e Serialização do Modelo 📊"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "block2_code",
            "metadata": {},
            "outputs": [],
            "source": [
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.model_selection import train_test_split\n",
                "from sklearn.metrics import classification_report\n",
                "import joblib as jl\n",
                "\n",
                "# Split de treino/teste estratificado para manter a proporção das classes\n",
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n",
                "\n",
                "model = RandomForestClassifier(n_estimators=100, random_state=42)\n",
                "model.fit(X_train, y_train)\n",
                "\n",
                "y_pred = model.predict(X_test)\n",
                "print(\"Métricas de Desempenho do Modelo:\")\n",
                "print(classification_report(y_test, y_pred, target_names=[\"legitimo\", \"risco\"]))\n",
                "\n",
                "# Serialização estável do artefato binário\n",
                "jl.dump(model, \"model.pkl\")\n",
                "print(\"✅ Artefato binário salvo como 'model.pkl'\")"
            ]
        },
        {
            "cell_type": "markdown",
            "id": "block3_title",
            "metadata": {},
            "source": [
                "--- \n",
                "# BLOCO 3 — Hugging Face Hub como Model Registry 🤗"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "block3_code",
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import sklearn\n",
                "from huggingface_hub import HfApi, login\n",
                "\n",
                "token = os.environ.get(\"HF_TOKEN\")\n",
                "if not token:\n",
                "    print(\"❌ Defina a variável 'HF_TOKEN' antes de rodar esta célula!\")\n",
                "else:\n",
                "    login(token=token)\n",
                "    api = HfApi()\n",
                "    username = api.whoami()[\"name\"]\n",
                "    repo_id = f\"{username}/mlops-bella-tavola-v1\"\n",
                "    \n",
                "    # Garante a existência do repositório remoto\n",
                "    api.create_repo(repo_id=repo_id, repo_type=\"model\", exist_ok=True)\n",
                "    \n",
                "    # Geração dinâmica do requirements do modelo\n",
                "    with open(\"requirements.txt\", \"w\") as f:\n",
                "        f.write(f\"scikit-learn=={sklearn.__version__}\\njoblib=={jl.__version__}\\nnumpy=={np.__version__}\\n\")\n",
                "        \n",
                "    # Escrita automatizada do Model Card (README.md)\n",
                "    model_card = f\"\"\"---\n",
                "language: pt\n",
                "tags:\n",
                "  - sklearn\n",
                "  - classification\n",
                "  - restaurante\n",
                "  - mlops\n",
                "---\n",
                "# Bella Tavola — Classificador de Risco de Pedidos 🍝\n",
                "\n",
                "Modelo preditivo para gerenciamento logístico e financeiro do restaurante Bella Tavola.\n",
                "\n",
                "## Contrato de Features\n",
                "1. `valor_pedido` (float)\n",
                "2. `hora_pedido` (int)\n",
                "3. `num_itens` (int)\n",
                "4. `historico_cancelamentos` (int)\n",
                "5. `distancia_entrega` (float)\n",
                "\"\"\"\n",
                "    with open(\"README_model.md\", \"w\", encoding=\"utf-8\") as f:\n",
                "        f.write(model_card)\n",
                "        \n",
                "    # Upload em lote dos metadados e binários para o registry\n",
                "    api.upload_file(path_or_fileobj=\"model.pkl\", path_in_repo=\"model.pkl\", repo_id=repo_id, repo_type=\"model\")\n",
                "    api.upload_file(path_or_fileobj=\"requirements.txt\", path_in_repo=\"requirements.txt\", repo_id=repo_id, repo_type=\"model\")\n",
                "    api.upload_file(path_or_fileobj=\"README_model.md\", path_in_repo=\"README.md\", repo_id=repo_id, repo_type=\"model\")\n",
                "    \n",
                "    if os.path.exists(\"README_model.md\"): os.remove(\"README_model.md\")\n",
                "    print(f\"🚀 Sucesso! Repositório publicado em: https://huggingface.co/{repo_id}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "id": "block4_title",
            "metadata": {},
            "source": [
                "--- \n",
                "# BLOCO 4 — Inferência Otimizada e Validação de Contrato 🛠️"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "block4_code",
            "metadata": {},
            "outputs": [],
            "source": [
                "from huggingface_hub import hf_hub_download\n",
                "import joblib\n",
                "import os\n",
                "\n",
                "def load_model(repo_id: str, filename: str = \"model.pkl\"):\n",
                "    token = os.environ.get(\"HF_TOKEN\")\n",
                "    local_path = hf_hub_download(repo_id=repo_id, filename=filename, token=token)\n",
                "    return joblib.load(local_path)\n",
                "\n",
                "try:\n",
                "    api = HfApi()\n",
                "    repo_id = f\"{api.whoami()['name']}/mlops-bella-tavola-v1\"\n",
                "    modelo_remoto = load_model(repo_id)\n",
                "    \n",
                "    # Teste de fumaça focado na ordem das colunas da API\n",
                "    amostra_teste = np.array([[120.0, 20, 3, 0, 2.5]])\n",
                "    pred = modelo_remoto.predict(amostra_teste)[0]\n",
                "    proba = modelo_remoto.predict_proba(amostra_teste)[0][1]\n",
                "    \n",
                "    print(f\"✅ Teste de Contrato Concluído!\")\n",
                "    print(f\"Predição: {pred} | Probabilidade de Risco: {proba:.4f}\")\n",
                "except Exception as e:\n",
                "    print(f\"❌ Erro na validação: {e}\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open("CDIA_CD2_2026_e03_bella_tavola.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=2, ensure_ascii=False)

print("🎉 Notebook 'CDIA_CD2_2026_e03_bella_tavola.ipynb' criado com sucesso na raiz do projeto!")