from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
import numpy as np

router = APIRouter()

# Definição do repositório oficial da aula no Hugging Face
REPO_ID = "joaogabriel101735/puc-sp-aula"
#REPO_ID = "joaogabriel101735/errado"
_model = None

def get_model():
    """
    Garante o carregamento Singleton do modelo para otimização de memória.
    """
    global _model
    if _model is None:
        from model_utils import load_model
        # O token é recuperado do ambiente, garantindo segurança
        _model = load_model(REPO_ID)
    return _model
# O modelo é carregado apenas na primeira chamada, otimizando o desempenho para múltiplas requisições subsequentes.
class PredictInput(BaseModel):
    """
    Schema de entrada com validações rigorosas via Pydantic.
    """
    custo_prato: float = Field(gt=0, description="Valor de custo dos insumos")
    dia_da_semana: int = Field(ge=0, le=6, description="Dia da semana (0-6)")
    hora_pedido: int = Field(ge=0, le=23, description="Hora do dia (0-23)")
    tempo_mesa: int = Field(ge=0, description="Estimativa de tempo de ocupação (min)")
    popularidade: float = Field(ge=1, le=5, description="Nota média do prato (1-5)")

class PredictOutput(BaseModel):
    """
    Schema de saída para garantir a consistência da resposta da API.
    """
    prediction: int
    probability: float
    label: str
    model_version: str

@router.post("/predict", response_model=PredictOutput)
async def predict(input: PredictInput):
    """
    Executa a predição de demanda utilizando o modelo carregado do Hub.
    """
    try:
        model = get_model()

        # A ordem das features deve ser rigorosamente a mesma do treino
        features = np.array([[
            input.custo_prato,
            input.dia_da_semana,
            input.hora_pedido,
            input.tempo_mesa,
            input.popularidade
        ]])

        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        label = "alta demanda" if prediction == 1 else "baixa demanda"

        return PredictOutput(
            prediction=prediction,
            probability=round(probability, 4),
            label=label,
            model_version=REPO_ID
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na inferência: {str(e)}")

@router.get("/health")
async def health(response: Response):
    """
    Endpoint de monitorização que distingue a saúde da API da disponibilidade do modelo.
    """
    try:
        # Tenta aceder ao modelo para validar a sua integridade
        model = get_model()
        # Teste rápido de inferência
        model.predict(np.zeros((1, 5)))
        
        return {
            "status": "ok",
            "model": "ok",
            "repo": REPO_ID
        }
    except Exception as e:
        # Retorna 200 com status degraded para manter a API online para outras funções
        response.status_code = 200
        return {
            "status": "ok",
            "model": "degraded",
            "detail": str(e)
        }