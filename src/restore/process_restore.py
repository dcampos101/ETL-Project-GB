import os
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery, storage
from google.api_core.exceptions import GoogleAPIError

from google.cloud.bigquery import WriteDisposition
app = FastAPI()

# Clean customer initialization
PROJECT_ID = "etl-gb-poc"
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)

print("Connected to BigQuery project:", bq_client.project)

bucket_name = "bkt-backup-tables"   # Bucket en GCS
local_backup_dir = "..\\backup\\backups"        # local folder where AVRO files are stored

os.makedirs(local_backup_dir, exist_ok=True)

@app.post("/restore/{table_name}")
def restore_table(table_name: str):
    dataset = "hresources"
    table_id = f"{PROJECT_ID}.{dataset}.{table_name}"
    local_path = os.path.join(local_backup_dir, f"{table_name}.avro")

    # Verify that the local backup file exists
    if not os.path.isfile(local_path):
        raise HTTPException(
            status_code=404, 
            detail=f"No local backup was found for the table '{table_name}' en {local_path}"
        )

    print("Starting restoration for:", table_id)

    try:
        # Configure the Load Job for BigQuery
        job_config = bigquery.LoadJobConfig(
            # Define that the input format is AVRO (maintains exact data types and schemas)
            source_format=bigquery.SourceFormat.AVRO,
            # WRITE_TRUNCATE replaces the data in the table if it already exists. 
            # If you prefer it to fail if the table exists, use WriteDisposition.WRITE_EMPTY
            write_disposition=WriteDisposition.WRITE_TRUNCATE 
        )

        # Read the local AVRO file and send it to BigQuery
        with open(local_path, "rb") as source_file:
            load_job = bq_client.load_table_from_file(
                source_file,
                table_id,
                job_config=job_config
            )
        
        # Wait for the BigQuery loading to finish.
        load_job.result()  
        print("Restoration successfully completed:", table_id)

        return {
            "status": "ok",
            "message": f"Table '{table_name}' restored successfully from the local backup.",
            "table_id": table_id
        }

    except GoogleAPIError as e:
        print(f"Error in Google Cloud API while restoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in BigQuery during restoration: {str(e)}")
        
    except Exception as e:
        print(f"Unexpected error during restoration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
