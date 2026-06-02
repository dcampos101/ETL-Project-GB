import os
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery, storage
from google.api_core.exceptions import GoogleAPIError

app = FastAPI()

# Inicialización limpia de clientes
PROJECT_ID = "etl-gb-poc"
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)

print("Connected to BigQuery project:", bq_client.project)

bucket_name = "bkt-backup-tables"   # Bucket en GCS
local_backup_dir = "backups"        # local folder where AVRO files are stored

os.makedirs(local_backup_dir, exist_ok=True)

@app.post("/backup/{table_name}")
def backup_table(table_name: str):
    dataset = "hresources"
    table_id = f"{PROJECT_ID}.{dataset}.{table_name}"
    destination_uri = f"gs://{bucket_name}/{table_name}.avro"

    print("Antes de extracción:", table_id)

    try:
        # Extraction Job Configuration
        job_config = bigquery.job.ExtractJobConfig(destination_format="AVRO")
        
        extract_job = bq_client.extract_table(
            table_id,
            destination_uri,
            job_config=job_config
        )
        
        # Wait for the process to finish in BigQuery
        extract_job.result()  
        print("Después de extracción con éxito:", table_id)

        # Download the generated AVRO file from GCS to local
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{table_name}.avro")
        local_path = os.path.join(local_backup_dir, f"{table_name}.avro")
        blob.download_to_filename(local_path)

        return {
            "status": "ok", 
            "message": "Backup completado exitosamente",
            "backup_file": local_path
        }

    except GoogleAPIError as e:
        # Captures specific Google Cloud errors (Tables not found, permissions, etc.)
        print(f"Error en Google Cloud API: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Error en recursos de GCP: {str(e)}")
        
    except Exception as e:
        # Captures other errors (e.g., write failures to the local disk)
        print(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
