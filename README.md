# Prueba Técnica: API REST de Cobros Simulados

Esta es la solución a la prueba técnica para la implementación de una API REST en Python (FastAPI) con MongoDB para la simulación de cobros y reembolsos.

#### El objetivo es permitir el CRUD de clientes y tarjetas, simular cobros, procesar reembolsos y consultar historiales, asegurando que no se almacenen PANs completos.

## 🚀 Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Framework API:** FastAPI
* **Base de Datos:** MongoDB (usando `pymongo`)
* **Validación:** Pydantic
* **Pruebas:** Pytest
* **Contenedorización:** Docker

---

## ⚙️ Configuración y Ejecución

Existen dos métodos para ejecutar el proyecto: con un entorno virtual o con Docker.

### Método 1: Entorno Virtual (Local)

**Requisitos:**
* Python 3.10+
* MongoDB corriendo en `mongodb://localhost:27017`

1.  **Clonar el repositorio:**
    ```bash
    git clone https://[URL-DE-TU-REPO].git
    cd prueba_tecnica
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (En Windows: venv\Scripts\activate)
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    uvicorn app.main:app --reload
    ```
    La API estará disponible en `http://127.0.0.1:8000`.

### Método 2: Docker

**Requisitos:**
* Docker y Docker Compose

1.  **Clonar el repositorio.**

2.  **Construir:**
    *Nota: El `Dockerfile` asume que MongoDB está accesible en `localhost`. Si corres Mongo en un contenedor, asegúrate de que la API pueda conectarse a él.*
    ```bash
    docker build -t api-cobros .
    ```
3. **Ejecutar:**
    ```bash
    docker run -p 8000:8000 --name cobros-api api-cobros
    ```
    La API estará disponible en `http://127.0.0.1:8000`.

---

## 🧪 Pruebas Unitarias y de Integración

El proyecto incluye una suite de pruebas con `pytest` que valida:
* El algoritmo de Luhn (generador y validador).
* El CRUD completo de Clientes.
* El CRUD completo de Tarjetas (con validación Luhn).
* El flujo de cobro (aprobado y rechazado).
* El flujo de reembolso.
* La consulta de historial.

Para ejecutar las pruebas:
```bash
pytest -v
```

---

## 📖 Documentación de la API (Swagger)

La API genera automáticamente la documentación interactiva (Swagger UI), pero también se incluye una colección completa de Postman para facilitar las pruebas.

Método 1: Swagger (Recomendado para explorar)

Una vez que la API esté corriendo, puedes acceder a la documentación completa para ver todos los endpoints y probar la API en vivo en:

```http request
http://127.0.0.1:8000/docs
```

Método 2: Colección de Postman (Recomendado para pruebas)

En la carpeta /postman del repositorio se incluyen los archivos:

    Prueba_Tecnica.postman_collection.json

    Prueba_Tecnica.postman_environment.json

Importa ambos archivos en Postman.
El entorno ya está configurado con una variable {{URL_BASE}} (fijada a http://127.0.0.1:8000) y separado por carpetas y peticiones para que se pueda ejecutar toda la suite de peticiones (Crear Cliente, Crear Tarjetas, Hacer Cobros, etc.) en orden, además se tiene configurado un script para guardar los id's (de cliente [idClient], de tarjeta [idCard], y de cobros [idCobro]) para que una vez que la respuesta sea exitosa se guarde el dato y pueda ser usado en las otras peticiones.

---

## 💳 Tarjetas de Prueba y Reglas de Simulación

Usa `POST /tarjetas` para crear tarjetas usando los siguientes PANs (todos son válidos según Luhn):

| PAN Completo (para crear) | `last4` | Regla de Simulación de Cobro |
| :--- | :--- | :--- |
| `4111111111111111` | `1111` | **Aprobado Siempre.** (Motivo: `00`) |
| `4000000000002222` | `2222` | **Rechazado Siempre.** (Motivo: `51` - Fondos Insuficientes) |
| `4000000000043333` | `3333` | **Límite de Monto:** Rechazado si el monto es > $1000. (Motivo: `61`) |
| *Cualquier otro* | `N/A` | Aprobado Siempre. (Motivo: `00`) |

---

## 📋 Historial de Cobros de Prueba

Se solicita un historial de cobros de prueba. Este historial se genera dinámicamente y se puede consultar en cualquier momento usando el endpoint:
```http request
GET /cobros/{cliente_id}
```

Este endpoint devolverá un arreglo JSON con todos los cobros (aprobados, declinados) y su estado de reembolso, cumpliendo con el requisito.
Ejemplo de respuesta:
```json
[
    {
        "_id": "691150f62c946db84301ee1c",
        "created_at": "2025-11-09T20:41:58.691000",
        "updated_at": "2025-11-09T20:47:38.395000",
        "cliente_id": "691150e22c946db84301ee18",
        "tarjeta_id": "691150ea2c946db84301ee1a",
        "monto": 1111.0,
        "fecha_intento": "2025-11-09T20:41:58.691000",
        "status": "approved",
        "codigo_motivo": "00",
        "reembolsado": true,
        "fecha_reembolso": "2025-11-09T20:47:38.395000"
    },
    {
        "_id": "6911512b2c946db84301ee20",
        "created_at": "2025-11-09T20:42:51.317000",
        "updated_at": "2025-11-09T20:42:51.317000",
        "cliente_id": "691150e22c946db84301ee18",
        "tarjeta_id": "6911510c2c946db84301ee1e",
        "monto": 2222.0,
        "fecha_intento": "2025-11-09T20:42:51.317000",
        "status": "declined",
        "codigo_motivo": "51",
        "reembolsado": false,
        "fecha_reembolso": null
    },
    {
        "_id": "6911514f2c946db84301ee24",
        "created_at": "2025-11-09T20:43:27.793000",
        "updated_at": "2025-11-09T20:43:27.793000",
        "cliente_id": "691150e22c946db84301ee18",
        "tarjeta_id": "6911513e2c946db84301ee22",
        "monto": 3333.0,
        "fecha_intento": "2025-11-09T20:43:27.793000",
        "status": "declined",
        "codigo_motivo": "61",
        "reembolsado": false,
        "fecha_reembolso": null
    },
    {
        "_id": "691151572c946db84301ee26",
        "created_at": "2025-11-09T20:43:35.422000",
        "updated_at": "2025-11-09T20:48:33.976000",
        "cliente_id": "691150e22c946db84301ee18",
        "tarjeta_id": "6911513e2c946db84301ee22",
        "monto": 333.0,
        "fecha_intento": "2025-11-09T20:43:35.422000",
        "status": "approved",
        "codigo_motivo": "00",
        "reembolsado": true,
        "fecha_reembolso": "2025-11-09T20:48:33.976000"
    },
    {
        "_id": "6911520e2c946db84301ee2c",
        "created_at": "2025-11-09T20:46:38.350000",
        "updated_at": "2025-11-09T20:46:38.350000",
        "cliente_id": "691150e22c946db84301ee18",
        "tarjeta_id": "691151fe2c946db84301ee2a",
        "monto": 4567.0,
        "fecha_intento": "2025-11-09T20:46:38.350000",
        "status": "approved",
        "codigo_motivo": "00",
        "reembolsado": false,
        "fecha_reembolso": null
    }
]
```
