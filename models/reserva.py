from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import datetime
from config import settings

class ReservaInput(BaseModel):
    # Validação dinâmica baseada no arquivo .env via config.settings
    mesa: int = Field(ge=1, le=settings.max_mesas)
    nome: str = Field(min_length=2, max_length=100)
    pessoas: int = Field(ge=1, le=settings.max_pessoas_por_mesa)
    data_hora: datetime

    @field_validator("data_hora")
    @classmethod
    def deve_ser_futura(cls, v, info: ValidationInfo):
        # Garante antecedência mínima de 1 hora (Caderno 02)
        agora = datetime.now(tz=v.tzinfo)
        if (v - agora).total_seconds() < 3600:
            raise ValueError("Reserva deve ser feita com pelo menos 1 hora de antecedência")
        return v

class ReservaOutput(BaseModel):
    id: int
    mesa: int
    nome: str
    pessoas: int
    data_hora: str
    ativa: bool
    criada_em: str