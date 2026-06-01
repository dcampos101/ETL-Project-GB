from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI(title="PoC Ingesta de Datos - Globant")

# 1. Definimos el esquema de datos que la API espera recibir (Validación automática)
class RegistroData(BaseModel):
    id_usuario: int
    monto: float
    categoria: str
    fecha: datetime = datetime.now() # Si no viene, usa la fecha actual

# Configuración de base de datos
CONN_STRING = "postgresql://usuario:password@localhost:5432/mi_db"
engine = create_engine(CONN_STRING)

# 2. Endpoint POST para recibir la información
@app.post("/v1/data/ingesta", status_code=201)
def recibir_nuevos_datos(data: RegistroData):
    try:
        # Convertimos el objeto recibido a un DataFrame de una sola fila
        nuevo_registro = pd.DataFrame([data.dict()])
        
        # Insertamos de inmediato en la base de datos
        nuevo_registro.to_sql('tabla_historica', con=engine, if_exists='append', index=False)
        
        return {"status": "success", "message": "Registro insertado correctamente"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar en base de datos: {str(e)}")

# Para ejecutar localmente: uvicorn nombre_archivo:app --reload
