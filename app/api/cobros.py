from fastapi import APIRouter, HTTPException, status, Body, Path
from app.core.db import db
from app.models import CobroCreate, Cobro, StatusCobro, Tarjeta
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from datetime import datetime
from typing import List

router = APIRouter()
collection = "cobros"
tarjetas_collection = "tarjetas"


def simular_cobro(tarjeta: Tarjeta, monto: float) -> (StatusCobro, str):
    """
    Función interna para aplicar las reglas de simulación definidas.
    Devuelve (status, codigo_motivo)
    """
    last4 = tarjeta.last4

    if last4 == "1111":
        return StatusCobro.approved, "00"
    elif last4 == "2222":
        return StatusCobro.declined, "51"
    elif last4 == "3333":
        if monto > 1000:
            return StatusCobro.declined, "61"
        else:
            return StatusCobro.approved, "00"
    else:
        return StatusCobro.approved, "00"


@router.post("/", response_model=Cobro, status_code=status.HTTP_201_CREATED, summary="Realizar un cobro simulado")
async def create_cobro(cobro_in: CobroCreate = Body(...)):
    """
    Realiza un cobro simulado sobre una tarjeta de prueba.

    Aplica las reglas de negocio (aprobación/rechazo) definidas basadas en los 'last4' de la tarjeta.
    """
    try:
        tarjeta_oid = ObjectId(cobro_in.tarjeta_id)
        cliente_oid = ObjectId(cobro_in.cliente_id)

        tarjeta = db[tarjetas_collection].find_one({"_id": tarjeta_oid})
        if tarjeta is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La tarjeta con ID {cobro_in.tarjeta_id} no existe.")

        tarjeta_modelo = Tarjeta.model_validate(tarjeta)

        if tarjeta_modelo.cliente_id != cliente_oid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La tarjeta no pertenece al cliente especificado.")

        status_cobro, motivo = simular_cobro(tarjeta_modelo, cobro_in.monto)

        cobro_data = {"cliente_id": cliente_oid, "tarjeta_id": tarjeta_oid, "monto": cobro_in.monto, "status": status_cobro, "codigo_motivo": motivo}

        cobro_db = Cobro.model_validate(cobro_data)

        insert_data = cobro_db.model_dump(by_alias=True, exclude=["id"])

        result = db[collection].insert_one(insert_data)

        created_cobro = db[collection].find_one({"_id": result.inserted_id})

        return Cobro.model_validate(created_cobro)
    except HTTPException as http_ex:
        raise http_ex
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error en la solicitud: {e}")


@router.post("/{cobro_id}/reembolso", response_model=Cobro, status_code=status.HTTP_200_OK, summary="Reembolsar un cobro")
async def create_reembolso(cobro_id: str = Path(..., alias="cobro_id")):
    """
    Reembolsa un cobro que haya sido previamente aprobado.
    Actualiza el estado 'reembolsado' a true y fija la 'fecha_reembolso'.
    """
    try:
        cobro_oid = ObjectId(cobro_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cobro inválido")

    cobro = db[collection].find_one({"_id": cobro_oid})

    if cobro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cobro con ID {cobro_id} no encontrado")

    cobro_modelo = Cobro.model_validate(cobro)

    if cobro_modelo.status == StatusCobro.declined:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No se puede reembolsar un cobro declinado.")

    if cobro_modelo.reembolsado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este cobro ya ha sido reembolsado.")

    update_data = {"reembolsado": True, "fecha_reembolso": datetime.now(), "updated_at": datetime.now()}

    result = db[collection].find_one_and_update({"_id": cobro_oid}, {"$set": update_data}, return_document=True)

    return Cobro.model_validate(result)


@router.get("/{cliente_id}", response_model=List[Cobro], status_code=status.HTTP_200_OK, summary="Obtener historial de cobros por cliente")
async def get_historial_por_cliente(cliente_id: str = Path(..., alias="cliente_id")):
    """
    Consulta todo el historial de cobros (aprobados, declinados y reembolsados) para un cliente específico.
    """
    try:
        cliente_oid = ObjectId(cliente_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cliente inválido")

    cursor = db[collection].find({"cliente_id": cliente_oid})

    historial = [Cobro.model_validate(doc) for doc in cursor]

    if not historial:
        pass

    return historial
