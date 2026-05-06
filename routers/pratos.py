from fastapi import APIRouter, HTTPException
from models.prato import PratoInput, PratoOutput, DisponibilidadeInput
from typing import Optional
from datetime import datetime

router = APIRouter()

pratos = [
    {"id": 1, "nome": "Margherita", "categoria": "pizza", "preco": 45.0, "preco_promocional": None, "descricao": "Clássica com molho de tomate, mussarela e manjericão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 2, "nome": "Carbonara", "categoria": "massa", "preco": 52.0, "preco_promocional": None, "descricao": "Espaguete com ovo, pecorino romano e guanciale", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 3, "nome": "Lasanha Bolonhesa", "categoria": "massa", "preco": 58.0, "preco_promocional": 49.0, "descricao": "Lasanha tradicional com ragù e molho bechamel", "disponivel": False, "criado_em": "2024-01-01T00:00:00"},
    {"id": 4, "nome": "Tiramisù", "categoria": "sobremesa", "preco": 28.0, "preco_promocional": None, "descricao": "Sobremesa com mascarpone, café e cacau", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 5, "nome": "Quattro Stagioni", "categoria": "pizza", "preco": 49.0, "preco_promocional": None, "descricao": "Pizza com quatro sabores clássicos italianos", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 6, "nome": "Panna Cotta", "categoria": "sobremesa", "preco": 24.0, "preco_promocional": None, "descricao": "Sobremesa italiana com creme e frutas vermelhas", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},

    {"id": 7, "nome": "Bruschetta Tradicional", "categoria": "entrada", "preco": 28.0, "preco_promocional": None, "descricao": "Pão italiano com tomate, alho, azeite e manjericão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 8, "nome": "Carpaccio de Carne", "categoria": "entrada", "preco": 42.0, "preco_promocional": None, "descricao": "Finas fatias de carne crua com rúcula e parmesão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 9, "nome": "Caprese", "categoria": "entrada", "preco": 35.0, "preco_promocional": None, "descricao": "Tomate, mussarela de búfala e manjericão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},

    {"id": 10, "nome": "Risoto de Funghi", "categoria": "risoto", "preco": 62.0, "preco_promocional": None, "descricao": "Arroz arbóreo com cogumelos e parmesão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 11, "nome": "Risoto alla Milanese", "categoria": "risoto", "preco": 68.0, "preco_promocional": None, "descricao": "Risoto com açafrão e manteiga", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 12, "nome": "Gnocchi ao Sugo", "categoria": "massa", "preco": 54.0, "preco_promocional": None, "descricao": "Nhoque de batata com molho de tomate", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 13, "nome": "Fettuccine Alfredo", "categoria": "massa", "preco": 56.0, "preco_promocional": None, "descricao": "Massa com molho cremoso de manteiga e parmesão", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 14, "nome": "Ravioli de Ricota e Espinafre", "categoria": "massa", "preco": 60.0, "preco_promocional": None, "descricao": "Massa recheada com ricota e espinafre ao molho de manteiga", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},

    {"id": 15, "nome": "Osso Buco", "categoria": "prato_principal", "preco": 85.0, "preco_promocional": None, "descricao": "Vitela cozida lentamente com legumes e vinho", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 16, "nome": "Saltimbocca alla Romana", "categoria": "prato_principal", "preco": 78.0, "preco_promocional": None, "descricao": "Vitela com presunto e sálvia ao vinho branco", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},

    {"id": 17, "nome": "Lula com Carne de Tubarão do Chef Leo Koide", "categoria": "prato_principal", "preco": 95.0, "preco_promocional": None, "descricao": "Lula recheada com carne de tubarão ao molho mediterrâneo", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    
    {"id": 18, "nome": "Sopa Alcoólica do Chef Cezar", "categoria": "sopa", "preco": 38.0, "preco_promocional": None, "descricao": "Sopa italiana com vinho branco, ervas e legumes", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},

    {"id": 19, "nome": "Minestrone", "categoria": "sopa", "preco": 32.0, "preco_promocional": None, "descricao": "Sopa tradicional italiana de legumes e massa", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 20, "nome": "Gelato Artesanal", "categoria": "sobremesa", "preco": 22.0, "preco_promocional": None, "descricao": "Sorvete italiano cremoso em diversos sabores", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
    {"id": 21, "nome": "Cannoli Siciliano", "categoria": "sobremesa", "preco": 26.0, "preco_promocional": None, "descricao": "Massa crocante recheada com ricota doce", "disponivel": True, "criado_em": "2024-01-01T00:00:00"},
]


@router.get("/", response_model=list[PratoOutput])
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False,
):
    resultado = pratos
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado


@router.get("/{prato_id}", response_model=PratoOutput)
async def buscar_prato(prato_id: int, formato: str = "completo"):
    for prato in pratos:
        if prato["id"] == prato_id:
            if formato == "resumido":
                return {**prato, "nome": prato["nome"], "preco": prato["preco"]}
            return prato
    raise HTTPException(status_code=404, detail=f"Prato com id {prato_id} não encontrado")


@router.post("/", response_model=PratoOutput, status_code=201)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump(),
    }
    pratos.append(novo_prato)
    return novo_prato


@router.put("/{prato_id}/disponibilidade", response_model=PratoOutput)
async def alterar_disponibilidade(prato_id: int, body: DisponibilidadeInput):
    for prato in pratos:
        if prato["id"] == prato_id:
            prato["disponivel"] = body.disponivel
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")
