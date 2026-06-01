from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, validator
from typing import List
from google.cloud import bigquery
import datetime

app = FastAPI()
client = bigquery.Client()

# Configura tus tablas en BigQuery
PROJECT_ID = "etl-gb-poc"
DATASET = "hresources"

# -----------------------------
# Modelos de validación
# -----------------------------
class Department(BaseModel):
    department_name: str

    @field_validator("department_name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("department_name is required")
        return v


class Job(BaseModel):
    job_title: str

    @field_validator("job_title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("job_title is required")
        return v


class Employee(BaseModel):
    name: str
    hire_date: datetime.datetime
    department_id: int
    job_id: int

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("name is required")
        return v


# -----------------------------
# Funciones para insertar en BigQuery
# -----------------------------
def insert_rows(table_name: str, rows: List[dict]):
    table_id = f"{PROJECT_ID}.{DATASET}.{table_name}"
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise HTTPException(status_code=400, detail=str(errors))
    return {"status": "ok", "rows": len(rows)}


# -----------------------------
# Endpoints
# -----------------------------
@app.post("/departments")
def insert_departments(departments: List[Department]):
    rows = [d.model_dump() for d in departments]
    return insert_rows("Departments", rows)


@app.post("/jobs")
def insert_jobs(jobs: List[Job]):
    rows = [j.model_dump() for j in jobs]
    return insert_rows("Jobs", rows)


@app.post("/employees")
def insert_employees(employees: List[Employee]):
    rows = [e.model_dump() for e in employees]
    return insert_rows("HiredEmployees", rows)
