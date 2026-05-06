from pydantic import BaseModel, Field


class BebidaInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    tipo: str = Field(pattern="^(vinho|agua|refrigerante|suco|cerveja)$")
    preco: float = Field(gt=0)
    alcoolica: bool
    volume_ml: int = Field(ge=50, le=2000)


class BebidaOutput(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str