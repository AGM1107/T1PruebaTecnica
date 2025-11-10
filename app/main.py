from fastapi import FastAPI
from app.core.db import db
from app.api import clientes, tarjetas, cobros
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    if db is None:
        print("ERROR: No se pudo conectar a la base de datos.")
    else:
        print("La aplicación ha iniciado y la conexión a DB está lista.")

    yield

    print("La aplicación se ha detenido.")


app = FastAPI(title="API de Cobros Simulados", description="Prueba Técnica para simular un CRUD de cobros.", version="1.0.0", lifespan=lifespan)


@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "Bienvenido a la API de Cobros Simulados"}

app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(tarjetas.router, prefix="/tarjetas", tags=["Tarjetas"])
app.include_router(cobros.router, prefix="/cobros", tags=["Cobros"])
