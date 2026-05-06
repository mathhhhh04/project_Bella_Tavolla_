from fastapi import APIRouter, HTTPException
from models.reserva import ReservaInput, ReservaOutput
from datetime import datetime
from typing import Optional

router = APIRouter()

reservas = []


@router.post("/", response_model=ReservaOutput, status_code=201)
async def criar_reserva(reserva: ReservaInput):
    data_reserva = reserva.data_hora.date()

    conflito = any(
        r["mesa"] == reserva.mesa
        and r["ativa"]
        and datetime.fromisoformat(r["data_hora"]).date() == data_reserva
        for r in reservas
    )
    if conflito:
        raise HTTPException(
            status_code=400,
            detail=f"Mesa {reserva.mesa} já está reservada para {data_reserva}",
        )

    nova = {
        "id": len(reservas) + 1,
        "mesa": reserva.mesa,
        "nome": reserva.nome,
        "pessoas": reserva.pessoas,
        "data_hora": reserva.data_hora.isoformat(),
        "ativa": True,
        "criada_em": datetime.now().isoformat(),
    }
    reservas.append(nova)
    return nova


@router.get("/", response_model=list[ReservaOutput])
async def listar_reservas(data: Optional[str] = None, apenas_ativas: bool = True):
    resultado = reservas
    if apenas_ativas:
        resultado = [r for r in resultado if r["ativa"]]
    if data:
        resultado = [
            r for r in resultado
            if datetime.fromisoformat(r["data_hora"]).date().isoformat() == data
        ]
    return resultado


@router.get("/mesa/{numero}", response_model=list[ReservaOutput])
async def reservas_por_mesa(numero: int):
    return [r for r in reservas if r["mesa"] == numero]


@router.get("/{reserva_id}", response_model=ReservaOutput)
async def buscar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            return r
    raise HTTPException(status_code=404, detail="Reserva não encontrada")


@router.delete("/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    for r in reservas:
        if r["id"] == reserva_id:
            if not r["ativa"]:
                raise HTTPException(status_code=400, detail="Reserva já está cancelada")
            r["ativa"] = False
            return {"mensagem": "Reserva cancelada com sucesso"}
    raise HTTPException(status_code=404, detail="Reserva não encontrada")