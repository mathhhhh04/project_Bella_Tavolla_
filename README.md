# Bella Tavola 🍝 — API & MLOps Pipeline

O **Bella Tavola** é uma API de produção desenvolvida em FastAPI focada no gerenciamento de risco e análise logística de pedidos para restaurantes de alta volumetria. O core da aplicação utiliza um modelo de Machine Learning (`RandomForestClassifier`) treinado com dados sintéticos aderentes ao negócio para predizer a probabilidade de um pedido ser problemático ou sofrer cancelamento antes de entrar na esteira de preparo.

O projeto adota práticas rigorosas de engenharia de software e MLOps, contando com um **Model Registry centralizado** no Hugging Face Hub e um **Pipeline de Integração Contínua (CI)** totalmente automatizado via GitHub Actions.

---

## 🛠️ Estrutura do Projeto

```text
project_Bella_Tavolla_/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline de CI/CD (3 Jobs independentes)
├── routers/
│   └── predict.py          # Rotas da API (/predict e /health do modelo)
├── tests/
│   ├── conftest.py         # Configuração de fixtures do pytest
│   └── test_modelo.py      # Suíte de testes (Smoke e Integração)
├── main.py                 # Ponto de entrada da aplicação FastAPI
├── train.py                # Script de geração de dados, treino e upload para o Hub
├── model_utils.py          # Utilitário de carregamento do modelo com cache local
├── .gitignore              # Proteção contra tracking de cache e arquivos .env
├── requirements.txt        # Dependências de produção e desenvolvimento
└── README.md               # Documentação principal da aplicação

🤖 O Modelo Preditivo & RegistryO modelo foi treinado mapeando comportamentos operacionais anômalos. O ciclo de vida do artefato é gerenciado externamente para que atualizações no modelo não requeiram novos deploys da API.Registry oficial: math04cezario/mlops-bella-tavola-v1Artefato gerado: model.pkl (Serializado via joblib)Contrato de Features (Ordem Rigorosa)Para mitigar desalinhamentos silenciosos de dados, a API monta a matriz de entrada seguindo estritamente a ordem usada no treinamento:#FeatureTipoDescrição1valor_pedidofloatValor total da compra em reais.2hora_pedidointHora em que o pedido foi computado (0-23).3num_itensintQuantidade total de pratos e itens no carrinho.4historico_cancelamentosintQuantidade de cancelamentos anteriores do cliente.5distancia_entregafloatDistância geográfica em km até o endereço de destino.⚡ Endpoints da API1. Predição de RiscoRota: POST /ml/predictPayload de Entrada:JSON{
  "valor_pedido": 350.0,
  "hora_pedido": 2,
  "num_itens": 8,
  "historico_cancelamentos": 3,
  "distancia_entrega": 18.5
}
Resposta Esperada (Status 200 OK):JSON{
  "prediction": 1,
  "probability": 1.0,
  "label": "risco",
  "model_version": "math04cezario/mlops-bella-tavola-v1"
}
2. Monitoramento de Saúde do ModeloRota: GET /ml/healthComportamento Resiliente: Avalia proativamente se o modelo está respondendo. Caso o repositório do Hugging Face esteja indisponível ou o token falhe, a API permanece no ar, mas o endpoint altera o status HTTP para 503 Service Unavailable e altera o nó do modelo para degraded, alertando os load balancers de produção.🚀 Pipeline de Integração Contínua (CI)A esteira automatizada do GitHub Actions garante a confiabilidade do sistema através de três jobs encadeados:Push ou PR para branch main
        │
        ▼
  ┌─────────────┐
  │  qualidade  │  ➔ Validação do Black + Autoflake + Testes Smoke (Rápido)
  └──────┬──────┘
         │
         ├─► (Apenas se passar e for um Push/Merge direto na branch main)
         ▼
  ┌─────────────┐
  │ integracao  │  ➔ Download seguro do modelo + Testes de Contrato e Endpoint
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  relatorio  │  ➔ Sumário de auditoria do commit e metadados do autor
  └─────────────┘
Job qualidade: Executa a checagem estática de formatação (black --check), remove códigos mortos e imports oclusos (autoflake) e roda os testes rápidos marcados como @pytest.mark.smoke.Job integracao: Executa em pushes na main. Baixa o modelo original do Hugging Face utilizando as credenciais credenciadas do repositório, aplica cache estratégico no diretório ~/.cache/huggingface para acelerar o pipeline e roda testes comportamentais completos (@pytest.mark.integracao).Job relatorio: Consolida as informações de sucesso do pipeline, identificando autor e Hash SHA do commit.🔧 Configuração e Execução Local1. Isolamento do Ambiente VirtualPara reproduzir perfeitamente o ambiente limpo do GitHub Runner sem interferência de pacotes globais da máquina, utilize:Bash# Criar e ativar o ambiente virtual isolado
python -m venv env_ci_test
source env_ci_test/bin/activate  # No Windows use: env_ci_test\Scripts\activate

# Atualizar gerenciador e instalar dependências do contrato
pip install --upgrade pip
pip install -r requirements.txt
2. Autenticação e Suíte de TestesDefina a variável de ambiente local com seu token de leitura do Hugging Face para que os testes de integração consigam carregar o artefato:Bash# Configurando credencial temporária no terminal
export HF_TOKEN="hf_seu_token_aqui"  # No PowerShell use: $env:HF_TOKEN="hf_seu_token_aqui"

# Rodar apenas testes rápidos estruturais (Smoke)
pytest tests/ -v -m smoke

# Rodar testes de integração completos simulando o pipeline de CI
pytest tests/ -v -m integracao --tb=short
🔒 Configurações de Segurança Obrigatórias no RepositórioPara o correto funcionamento do pipeline de CI, configure as credenciais secretas nas diretrizes do seu repositório no GitHub:Acesse seu repositório no GitHub.Vá em Settings ➔ Secrets and variables ➔ Actions.Clique em New repository secret.Crie o segredo abaixo:Name: HF_TOKENSecret: (Cole seu token do Hugging Face com permissão de leitura/write)Nota: Os secrets nunca são expostos nos logs de execução do GitHub Actions, sendo mascarados automaticamente com ***.
