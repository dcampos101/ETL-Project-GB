from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List
from google.cloud import bigquery

app = FastAPI()
client = bigquery.Client(project="etl-gb-poc")

table_id = "etl-gb-poc.hresources.departments"

# Modelo de entrada
class Department(BaseModel):
    department_name: str

    @field_validator("department_name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("department_name is required")
        return v

# Función para obtener el siguiente department_id
def get_next_department_id():
    query = f"SELECT MAX(department_id) as max_id FROM `{table_id}`"
    results = client.query(query).result()
    for row in results:
        return (row.max_id or 0) + 1
    return 1

# Endpoint para insertar departamentos
@app.post("/departments")
def insert_departments(departments: List[Department]):
    rows = []
    for d in departments:
        next_id = get_next_department_id()
        rows.append({
            "department_id": next_id,
            "department_name": d.department_name
        })

    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise HTTPException(status_code=400, detail=str(errors))

    return {"status": "ok", "rows": len(rows), "inserted": rows}

# Endpoint raíz para verificar que la API funciona
@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}
