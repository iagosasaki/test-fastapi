from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao
from schemas import PedidoSchema
from sqlalchemy.orm import Session
from models import Pedido

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def get_orders():
    """
    Retrieve a list of orders.
    """
    return {"message": "List of orders"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return HTTPException(status_code=201, detail=f"message: Pedido criado com sucesso. Id do pedido: {novo_pedido.id}")