import os
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery

app = FastAPI(title="Recruitment report - Globant PoC")

bq_client = bigquery.Client()

# =====================================================================#
#Endpoint hires-employees: Number of employees hired per quarter in 2021, by department and job
@app.get("/hires-employees", status_code=200)
def obtain_hires_per_quarter():
    try:
        # We define the structured analytical query
        query = """
            SELECT 
                d.department_name,
                j.job_title,
                SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 1 THEN 1 ELSE 0 END) AS Q1,
                SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 2 THEN 1 ELSE 0 END) AS Q2,
                SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 3 THEN 1 ELSE 0 END) AS Q3,
                SUM(CASE WHEN EXTRACT(QUARTER FROM CAST(e.hire_date AS TIMESTAMP)) = 4 THEN 1 ELSE 0 END) AS Q4
            FROM 
                `etl-gb-poc.hresources.hired_employees` e
            INNER JOIN 
                `etl-gb-poc.hresources.departments` d ON e.department_id = d.department_id
            INNER JOIN 
                `etl-gb-poc.hresources.jobs` j ON e.job_id = j.job_id
            WHERE 
                EXTRACT(YEAR FROM CAST(e.hire_date AS TIMESTAMP)) = 2021
            GROUP BY 
                d.department_name, j.job_title
            ORDER BY 
                d.department_name ASC, j.job_title ASC;
        """
        
        # We execute the query in BigQuery
        query_job = bq_client.query(query)
        resultados = query_job.result()
        
        # format the response to a clean JSON dictionary list
        respond = []
        for row in resultados:
            respond.append({
                "department": row.department_name,
                "job": row.job_title,
                "Q1": row.Q1,
                "Q2": row.Q2,
                "Q3": row.Q3,
                "Q4": row.Q4
            })
            
        return respond

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating metrics in BigQuery: {str(e)}"
        )
    
# =====================================================================#
#Endpoint hires-employees: Departments 
@app.get("/hires-departments", status_code=200)
def obtain_top_departments():
    try:
        query = """
            WITH contrataciones_por_depto AS (
                SELECT 
                    d.department_id AS id_departamento,
                    d.department_name AS nombre_departamento,
                    COUNT(e.employee_id) AS total_contratados
                FROM 
                    `etl-gb-poc.hresources.departments` d
                INNER JOIN 
                    `etl-gb-poc.hresources.hired_employees` e ON e.department_id = d.department_id
                WHERE 
                    EXTRACT(YEAR FROM CAST(e.hire_date AS TIMESTAMP)) = 2021
                GROUP BY 
                    d.department_id, d.department_name
            )
            SELECT 
                id_departamento AS id,
                nombre_departamento AS name,
                total_contratados AS hired
            FROM 
                contrataciones_por_depto
            WHERE 
                total_contratados > (SELECT AVG(total_contratados) FROM contrataciones_por_depto)
            ORDER BY 
                total_contratados DESC;
        """
        
        query_job = bq_client.query(query)
        resultados = query_job.result()
        
        respond = []
        for row in resultados:
            respond.append({
                "id": row.id,
                "name": row.name,
                "hired": row.hired
            })
            
        return respond

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating top departments in BigQuery: {str(e)}"
        )