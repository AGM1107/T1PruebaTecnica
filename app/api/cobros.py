from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_all_cobros():
    return {"message": "Endpoint de Cobros (GET) - Pendiente"}