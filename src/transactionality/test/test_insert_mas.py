from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from datetime import datetime, timedelta

app = FastAPI()
client = bigquery.Client(project="etl-gb-poc")

employees_table = "etl-gb-poc.hresources.hired_employees"

def get_next_employee_id():
    query = f"SELECT MAX(employee_id) as max_id FROM `{employees_table}`"
    results = client.query(query).result()
    for row in results:
        return (row.max_id or 0) + 1
    return 1

@app.post("/test_batch_insert")
def test_batch_insert():
    rows = []
    base_date = datetime(2026, 6, 1, 9, 0, 0)

    # Generate 1000 fictitious records
    next_id = get_next_employee_id()
    for i in range(1, 1001):
        rows.append({
            "employee_id": next_id + i - 1,
            "name": f"Empleado_{i}",
            "hire_date": (base_date + timedelta(minutes=i)).isoformat(),
            "department_id": (i % 10) + 1,  # IDs de 1 a 10
            "job_id": (i % 5) + 1           # IDs de 1 a 5
        })

    # Insertar en BigQuery
    errors = client.insert_rows_json(employees_table, rows)
    if errors:
        raise HTTPException(status_code=400, detail=str(errors))

    return {"status": "ok", "rows": len(rows)}
