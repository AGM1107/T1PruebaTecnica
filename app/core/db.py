from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "prueba_tecnica_cobros"


try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    client.server_info()
    print("Conexión a MongoDB establecida con éxito.")

    db = client[DATABASE_NAME]
except Exception as e:
    print(f"Error al conectar con MongoDB: {e}")
    db = None
