from fastapi import APIRouter, HTTPException, status, Body, Path
from app.core.db import db
from app.models import TarjetaCreate, TarjetaUpdate, Tarjeta
from app.luhn import validate_luhn
from pydantic import ValidationError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from pymongo.results import DeleteResult
from datetime import datetime

router = APIRouter()
collection = "tarjetas"
clientes_collection = "clientes"


@router.post("/", response_model=Tarjeta, status_code=status.HTTP_201_CREATED, summary="Registrar una tarjeta de prueba")
async def create_tarjeta(tarjeta_in: TarjetaCreate = Body(...)):
    """
    [cite_start]Registra una nueva tarjeta de prueba para un cliente[cite: 23].

    - [cite_start]Valida el PAN completo usando el algoritmo de Luhn[cite: 23].
    - [cite_start]NO guarda el PAN completo, solo el 'bin', 'last4' y 'pan_masked'[cite: 14, 16, 24].
    """
    if not validate_luhn(tarjeta_in.pan_completo):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de tarjeta (PAN) no es válido según el algoritmo de Luhn.")

    try:
        cliente_oid = ObjectId(tarjeta_in.cliente_id)
        cliente = db[clientes_collection].find_one({"_id": cliente_oid})
        if cliente is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El cliente con ID {tarjeta_in.cliente_id} no existe.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cliente inválido")

    try:
        pan = tarjeta_in.pan_completo

        tarjeta_db_data = {"cliente_id": cliente_oid, "pan_masked": f"************{pan[-4:]}", "last4": pan[-4:], "bin": pan[:6]}

        tarjeta_db = Tarjeta.model_validate(tarjeta_db_data)

        insert_data = tarjeta_db.model_dump(by_alias=True, exclude=["id"])

        result = db[collection].insert_one(insert_data)

        created_tarjeta = db[collection].find_one({"_id": result.inserted_id})

        return Tarjeta.model_validate(created_tarjeta)

    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos: {e}")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Datos de tarjeta inválidos: {e}")


@router.get("/{id}", response_model=Tarjeta, status_code=status.HTTP_200_OK, summary="Obtener una tarjeta por ID")
async def get_tarjeta_by_id(id: str = Path(..., alias="id")):
    """
    [cite_start]Obtiene los detalles de una tarjeta (enmascarada) por su ID[cite: 25].
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarjeta inválido")

    tarjeta = db[collection].find_one({"_id": object_id})

    if tarjeta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarjeta con ID {id} no encontrada")

    return Tarjeta.model_validate(tarjeta)


@router.put("/{id}",response_model=Tarjeta, status_code=status.HTTP_200_OK, summary="Actualizar metadatos de una tarjeta (si aplica)")
async def update_tarjeta(id: str = Path(..., alias="id"), update_data: TarjetaUpdate = Body(...)):
    """
    Actualiza metadatos de una tarjeta. El PDF especifica
    [cite_start]que el PAN completo no debe ser actualizable[cite: 26].
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarjeta inválido")

    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        tarjeta_actual = db[collection].find_one({"_id": object_id})
        if tarjeta_actual is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarjeta con ID {id} no encontrada")
        return Tarjeta.model_validate(tarjeta_actual)

    update_dict["updated_at"] = datetime.now()
    result = db[collection].find_one_and_update({"_id": object_id}, {"$set": update_dict}, return_document=True)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarjeta con ID {id} no encontrada")

    return Tarjeta.model_validate(result)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una tarjeta por ID")
async def delete_tarjeta(id: str = Path(..., alias="id")):
    """
    [cite_start]Elimina una tarjeta de la base de datos[cite: 27].
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarjeta inválido")

    result: DeleteResult = db[collection].delete_one({"_id": object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarjeta con ID {id} no encontrada")

    return
