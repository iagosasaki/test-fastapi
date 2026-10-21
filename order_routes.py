from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema
from sqlalchemy.orm import Session
from models import Pedido, Usuario, ItemPedido

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

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
    return {"message": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a cancelar este pedido")

    pedido.status = "CANCELADO"
    session.commit()
    return {"message": f"Pedido {id_pedido} cancelado com sucesso."}

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a listar pedidos")

    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()

    return {"pedidos": pedidos}

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(itemPedidoSchema: ItemPedidoSchema, id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a adicionar itens a pedidos")

    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    item = ItemPedido(
        quantidade=itemPedidoSchema.quantidade,
        sabor=itemPedidoSchema.sabor,
        tamanho=itemPedidoSchema.tamanho,
        preco_unitario=itemPedidoSchema.preco_unitario,
        pedido=id_pedido
    )

    session.add(item)
    pedido.calcular_preco() 
    session.commit()
    return {"message": f"Item adicionado ao pedido {id_pedido} com sucesso."}

@order_router.post("/pedido/remover-item/{id_item}")
async def remover_item_pedido(id_item: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a remover itens de pedidos")
    item = session.query(ItemPedido).filter(ItemPedido.id == id_item).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    pedido = session.query(Pedido).filter(Pedido.id == item.pedido).first()
    
    session.delete(item)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido do pedido com sucesso.",
        "quantidade": len(pedido.item),
        "pedido": pedido
    }

#finalizar um pedido
@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a finalizar este pedido")

    pedido.status = "FINALIZADO"
    session.commit()
    return {"message": f"Pedido {id_pedido} finalizado com sucesso."}

#visualizar 1 pedido
@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Usuário não autorizado a consultar o pedido")

    return {
        "pedido": pedido 
    }

#visualizar todos os pedidos de um usuario
@order_router.get("/listar-todos")
async def listar_todos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).join(ItemPedido).filter(Pedido.usuario == usuario.id).all()

    if pedidos is None:
        return {
            "Message": "Nenhum pedido foi encontrado para o usuário"
        }

    
    pedidosResponse = []
    for pedido in pedidos:
        for item in pedido.item:
            itemResponse = {
                "pedido": pedido.id,
                "id": item.id,
                "quantidade": item.quantidade,
                "sabor": item.sabor,
                "tamanho": item.tamanho,
                "preco_unitario": item.preco_unitario
            }
            pedidosResponse.append(itemResponse)
    
    return {
        "pedido": pedidosResponse
    }