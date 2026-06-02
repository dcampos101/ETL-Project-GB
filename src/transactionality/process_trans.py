from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List
from google.cloud import bigquery
from datetime import datetime
import datetime

app = FastAPI()
client = bigquery.Client()

print("Connected to BigQuery:", client.project)

table_id_departments = "etl-gb-poc.hresources.departments"
table_id_jobs = "etl-gb-poc.hresources.jobs"
table_id_hemployees = "etl-gb-poc.hresources.hired_employees"

# Configura tus tablas en BigQuery
#PROJECT_ID = "etl-gb-poc"
#DATASET = "hresources"

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

# -----------------------------
# Function to obtain the maximum department_id
# -----------------------------
def get_next_department_id():
    query = f"SELECT MAX(department_id) as max_id FROM `{table_id_departments}`"
    results = client.query(query).result()
    for row in results:
        return (row.max_id or 0) + 1
    return 1

class Job(BaseModel):
    job_title: str

    @field_validator("job_title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("job_title is required")
        return v

# -----------------------------
# Function to obtain the maximum job_id
# -----------------------------
def get_next_job_id():
    query = f"SELECT MAX(job_id) as max_id FROM `{table_id_jobs}`"
    results = client.query(query).result()
    for row in results:
        return (row.max_id or 0) + 1
    return 1

class Employee(BaseModel):
    name: str
    hire_date: str
    department_id: int
    job_id: int

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("name is required")
        return v
    
    #@field_validator("hire_date")
    #def validate_hire_date(cls, v):
    #    if not v.strip():
    #        raise ValueError("hire_date is required")
    #    return v

from datetime import datetime

def validate_date(fecha_str: str) -> datetime:
    """
    Validates that the date is in YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, or YYYY-MM-DDTHH:MM:SZ format
    and returns a datetime object.
    """
    formatos = ["%Y-%m-%d","%Y-%m-%dT%H:%M:%S","%Y-%m-%dT%H:%M:%SZ"]
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str, fmt)
        except ValueError:
            continue
    raise ValueError("hire_date must be formatted YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS o YYYY-MM-DDTHH:MM:SZ")

# Funciones de validación
def department_exists(department_id: int) -> bool:
    query = f"SELECT COUNT(1) as cnt FROM `{table_id_departments}` WHERE department_id = {department_id}"
    result = client.query(query).result()
    for row in result:
        return row.cnt > 0
    return False

def job_exists(job_id: int) -> bool:
    query = f"SELECT COUNT(1) as cnt FROM `{table_id_jobs}` WHERE job_id = {job_id}"
    result = client.query(query).result()
    for row in result:
        return row.cnt > 0
    return False

# -----------------------------
# Function to obtain the maximum employee_id
# -----------------------------
def get_next_employee_id():
    query = f"SELECT MAX(employee_id) as max_id FROM `{table_id_hemployees}`"
    results = client.query(query).result()
    for row in results:
        return (row.max_id or 0) + 1
    return 1

# -----------------------------
# Endpoints departments
# -----------------------------
@app.post("/departments")
def insert_departments(departments: List[Department]):
    rows = []
    for d in departments:
        next_id = get_next_department_id()
        rows.append({
            "department_id": next_id,
            "department_name": d.department_name
        })

    errors = client.insert_rows_json(table_id_departments, rows)
    if errors:
        raise HTTPException(status_code=400, detail=str(errors))

    return {"status": "ok", "rows": len(rows), "inserted": rows}

# -----------------------------
# Endpoints jobs
# -----------------------------
@app.post("/jobs")
def insert_jobs(jobs: List[Job]):
    rows = []
    for j in jobs:
        next_id = get_next_job_id()
        rows.append({
            "job_id": next_id,
            "job_title": j.job_title
        })

    errors = client.insert_rows_json(table_id_jobs, rows)
    if errors:
        raise HTTPException(status_code=400, detail=str(errors))

    return {"status": "ok", "rows": len(rows), "inserted": rows}

# -----------------------------
# Endpoints employees
# -----------------------------
@app.post("/employees")
def insert_employees(employees: List[Employee]):
    if len(employees) < 1 or len(employees) > 1000:
                    raise HTTPException(status_code=400, detail="You must submit between 1 and 1000 records")
    rows = []
    for e in employees:
        try:
            hire_date1 = validate_date(e.hire_date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if not department_exists(e.department_id):
            raise HTTPException(status_code=400, detail=f"Department ID {e.department_id} does not exist")
        if not job_exists(e.job_id):
            raise HTTPException(status_code=400, detail=f"Job ID {e.job_id} does not exist")
        
        next_id = get_next_employee_id()
        rows.append({
            "employee_id": next_id,
            "name": e.name,
            "hire_date": hire_date1.isoformat(),
            "department_id": e.department_id,
            "job_id": e.job_id
        })

    try:
        errors = client.insert_rows_json(table_id_hemployees, rows)
        if errors:
            raise HTTPException(status_code=400, detail=str(errors))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando empleado: {str(e)}")

    return {"status": "ok", "rows": len(rows), "inserted": rows}

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}