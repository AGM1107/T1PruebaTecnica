from pydantic import BaseModel, Field, EmailStr
from pydantic_mongo import ObjectIdField
from datetime import datetime
from typing import Optional
from enum import Enum


class ClienteBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str


class TarjetaCreate(BaseModel):
    cliente_id: str
    pan_completo: str = Field(..., min_length=13, max_length=19)


class CobroCreate(BaseModel):
    tarjeta_id: str
    cliente_id: str
    monto: float = Field(..., gt=0)


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None


class TarjetaUpdate(BaseModel):
    pass


class MongoModel(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectIdField: str}


class StatusCobro(str, Enum):
    approved = "approved"
    declined = "declined"


class Cobro(MongoModel):
    cliente_id: ObjectIdField
    tarjeta_id: ObjectIdField
    monto: float
    fecha_intento: datetime = Field(default_factory=datetime.now)
    [cite_start]status: StatusCobro[cite: 15]
    [cite_start]codigo_motivo: Optional[str] = None[cite: 15]
    [cite_start]reembolsado: bool = Field(default=False)[cite: 15]
    [cite_start]fecha_reembolso: Optional[datetime] = None[cite: 15]


class Tarjeta(MongoModel):
    cliente_id: ObjectIdField
    [cite_start]pan_masked: str[cite: 14]
    [cite_start]last4: str[cite: 14]
    [cite_start]bin: str[cite: 14]


class Cliente(MongoModel):
    nombre: str
    email: EmailStr
    telefono: str
