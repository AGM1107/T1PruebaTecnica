from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_all_clientes():
    return {"message": "Endpoint de Clientes (GET) - Pendiente"}