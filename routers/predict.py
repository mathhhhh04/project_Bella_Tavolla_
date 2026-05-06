from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np
import os

router = APIRouter()

# OBS: O código tenta ler seu usuário do ambiente ou assume o padrão configurado
HF_USER = os.environ.get("USER", "mathhhhh04") 
REPO_ID = "math04cezario/mlops-bella-tavola-v1"
_model = None

def get_model():
    global _model
    if _model is None:
        from model_utils import load_model
        _model = load_model(REPO_ID)
    return _model

class PredictInput(BaseModel):
    valor_pedido: float = Field(gt=0, description="Valor do pedido em reais")
    hora_pedido: int = Field(ge=0, le=23, description="Hora do dia")
    num_itens: int = Field(gt=0, description="Quantidade de pratos")
    historico_cancelamentos: int = Field(ge=0, description="Cancelamentos prévios")
    distancia_entrega: float = Field(ge=0, description="Distância em km")

class PredictOutput(BaseModel):
    prediction: int
    probability: float
    label: str
    model_version: str

@router.post("/predict", response_model=PredictOutput)
async def predict(input: PredictInput):
    model = get_model()

    # Ordem rigorosa idêntica à ordem de colunas do treinamento
    features = np.array([[
        input.valor_pedido,
        input.hora_pedido,
        input.num_itens,
        input.historico_cancelamentos,
        input.distancia_entrega
    ]])

    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    label = "risco" if prediction == 1 else "legítimo"

    return PredictOutput(
        prediction=prediction,
        probability=round(probability, 4),
        label=label,
        model_version=REPO_ID
    )

@router.get("/health")
async def health():
    """
    Health check proativo: diferencia API online de modelo quebrado/indisponível.
    """
    try:
        model = get_model()
        test_input = np.zeros((1, 5))
        model.predict(test_input)
        model_ok = True
        detail = None
    except Exception as e:
        model_ok = False
        detail = str(e)

    body = {
        "api": "ok",
        "model": "ok" if model_ok else "degraded",
        "model_repo": REPO_ID,
        "detail": detail
    }

    # 503 se o modelo falhar (informa load balancers para não direcionar requisições de ML)
    status_code = status.HTTP_200_OK if model_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=body, status_code=status_code)
