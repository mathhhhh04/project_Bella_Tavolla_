from fastapi import APIRouter, HTTPException
from models.pedido import PedidoInput, PedidoOutput
from routers.pratos import pratos
import numpy as np

router = APIRouter()
pedidos = []

def obter_preco_ia(prato_id: int):
    """
    Consome o modelo carregado em memória para sugerir um preço dinâmico.
    """
    try:
        # Importação local para evitar imports circulares e usar o Singleton
        from routers.predict import get_model
        model = get_model()
        
        # Simulamos as features de entrada para o modelo (Exemplo: alta popularidade e fim de semana)
        # Num cenário real, buscaríamos os dados históricos deste prato_id
        features = np.array([[30.0, 5, 20, 45, 4.8]]) 
        
        # Executa a inferência localmente (milissegundos)
        prediction = model.predict(features)[0]
        
        # Lógica de Negócio: Se a demanda prevista for alta (1), aplica um acréscimo de 10%
        if prediction == 1:
            prato_atual = next((p for p in pratos if p["id"] == prato_id), None)
            return float(prato_atual["preco"] * 1.10) if prato_atual else None
            
        return None
    except Exception:
        # Em caso de falha no modelo, o sistema ignora silenciosamente a IA
        return None

@router.post("/", response_model=PedidoOutput, status_code=201)
async def criar_pedido(pedido: PedidoInput):
    """
    Cria um pedido validando a existência do prato e aplicando a precificação dinâmica.
    """
    # 1. Validação de existência e disponibilidade
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)
    
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    
    if not prato["disponivel"]:
        raise HTTPException(status_code=400, detail=f"O prato '{prato['nome']}' não está disponível")

    # 2. Motor de Precificação (Hierarquia MLOps): IA > Promocional > Base
    preco_ia = obter_preco_ia(pedido.prato_id)
    preco_efetivo = preco_ia or prato["preco_promocional"] or prato["preco"]

    # 3. Persistência do pedido
    novo_pedido = {
        "id": len(pedidos) + 1,
        "prato_id": pedido.prato_id,
        "nome_prato": prato["nome"],
        "quantidade": pedido.quantidade,
        "valor_total": round(preco_efetivo * pedido.quantidade, 2),
        "observacao": pedido.observacao,
    }
    
    pedidos.append(novo_pedido)
    return novo_pedido

@router.get("/", response_model=list[PedidoOutput])
async def listar_pedidos():
    """
    Retorna a listagem de todos os pedidos realizados.
    """
    return pedidos