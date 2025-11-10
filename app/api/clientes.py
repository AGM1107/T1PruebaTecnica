from fastapi import APIRouter, HTTPException, status, Body, Path
from app.core.db import db
from app.models import ClienteBase, ClienteUpdate, Cliente
from pydantic import ValidationError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from pymongo.results import DeleteResult
from datetime import datetime

router = APIRouter()
collection = "clientes"


@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo cliente")
async def create_cliente(cliente: ClienteBase = Body(...)):
    """
    Crea un nuevo cliente en la base de datos.
    """
    try:
        cliente_dict = cliente.model_dump()

        result = db[collection].insert_one(cliente_dict)

        created_cliente = db[collection].find_one({"_id": result.inserted_id})

        return Cliente.model_validate(created_cliente)
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en la base de datos: {e}")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Datos de cliente inválidos: {e}")


@router.get("/{id}", response_model=Cliente, status_code=status.HTTP_200_OK, summary="Obtener un cliente por ID")
async def get_cliente_by_id(id: str = Path(..., alias="id")):
    """
    Obtiene los detalles de un cliente específico por su ID.
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cliente inválido")

    cliente = db[collection].find_one({"_id": object_id})

    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente con ID {id} no encontrado")

    return Cliente.model_validate(cliente)


@router.put("/{id}", response_model=Cliente, status_code=status.HTTP_200_OK, summary="Actualizar un cliente por ID")
async def update_cliente(id: str = Path(..., alias="id"), update_data: ClienteUpdate = Body(...)):
    """
    Actualiza la información de un cliente existente.
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cliente inválido")

    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se proporcionaron datos para actualizar")

    update_dict["updated_at"] = datetime.now()

    result = db[collection].find_one_and_update(
        {"_id": object_id},
        {"$set": update_dict},
        return_document=True
    )

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente con ID {id} no encontrado")

    return Cliente.model_validate(result)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un cliente por ID")
async def delete_cliente(id: str = Path(..., alias="id")):
    """
    Elimina un cliente de la base de datos.
    """
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de cliente inválido")

    result: DeleteResult = db[collection].delete_one({"_id": object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente con ID {id} no encontrado")

    return
