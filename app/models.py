from pydantic import BaseModel, Field, EmailStr
from pydantic_mongo import ObjectIdField
from datetime import datetime
from typing import Optional
from enum import Enum


class ClienteBase(BaseModel):
    """Modelo base para un cliente, usado para creación (POST)."""
    nombre: str
    email: EmailStr
    telefono: str


class TarjetaCreate(BaseModel):
    """Modelo para registrar una nueva tarjeta."""
    cliente_id: str
    pan_completo: str = Field(..., min_length=13, max_length=19)


class CobroCreate(BaseModel):
    """Modelo para crear un nuevo cobro."""
    tarjeta_id: str
    cliente_id: str
    monto: float = Field(..., gt=0)


class ClienteUpdate(BaseModel):
    """Modelo para actualizar un cliente. Todos los campos son opcionales."""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None


class TarjetaUpdate(BaseModel):
    """
    Modelo para actualizar metadatos de tarjeta.
    No se debe actualizar el PAN.
    """
    pass


class MongoModel(BaseModel):
    """Modelo base para todos los documentos en MongoDB."""
    id: ObjectIdField = Field(default_factory=ObjectIdField, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectIdField: str}


class StatusCobro(str, Enum):
    """Define los estados posibles de un cobro."""
    approved = "approved"
    declined = "declined"


class Cobro(MongoModel):
    """Modelo completo de Cobro como se guarda en la BD."""
    cliente_id: ObjectIdField
    tarjeta_id: ObjectIdField
    monto: float
    fecha_intento: datetime = Field(default_factory=datetime.now)
    status: StatusCobro
    codigo_motivo: Optional[str] = None
    reembolsado: bool = Field(default=False)
    fecha_reembolso: Optional[datetime] = None


class Tarjeta(MongoModel):
    """Modelo completo de Tarjeta como se guarda en la BD."""
    cliente_id: ObjectIdField
    pan_masked: str
    last4: str
    bin: str


class Cliente(MongoModel):
    """Modelo completo de Cliente como se guarda en la BD."""
    nombre: str
    email: EmailStr
    telefono: str
