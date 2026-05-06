from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional

class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    preco_promocional: Optional[float] = Field(default=None, gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True

    @field_validator("preco_promocional")
    @classmethod
    def validar_preco_promocional(cls, v, info: ValidationInfo):
        if v is None:
            return v
        if "preco" not in info.data:
            return v
        
        preco_original = info.data["preco"]
        if v >= preco_original:
            raise ValueError("Preço promocional deve ser menor que o preço original")
        
        desconto = (preco_original - v) / preco_original
        if desconto > 0.5:
            raise ValueError("Desconto não pode ser maior que 50% do preço original")
        return v

class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    preco_promocional: Optional[float]
    descricao: Optional[str]
    disponivel: bool
    criado_em: str

class DisponibilidadeInput(BaseModel):
    disponivel: bool