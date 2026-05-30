import requests
import pandas as pd
from google.cloud import storage
import io

def upload_from_github(bucket_name, github_urls):
    """Descarga varios archivos desde GitHub y los sube a GCS"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for url, config in github_urls.items():
        # Descargar archivo desde GitHub
        response = requests.get(url)
        response.raise_for_status()

        # Subir directamente desde memoria
        blob = bucket.blob(config)
        blob.upload_from_string(response.content, content_type="text/csv")
        

        #print(f"Archivo {url} subido a gs://{bucket_name}/{config['destination']}")
        print(f"Archivo {url} subido a gs://{bucket_name}/{config}")

# Ejemplo de uso
github_files = {
    "https://github.com/dcampos101/ETL-Project-GB/blob/main/files/departments.csv": "departments.csv",
    "https://github.com/dcampos101/ETL-Project-GB/blob/main/files/hired_employees.csv": "hired_employees.csv",
    "https://github.com/dcampos101/ETL-Project-GB/blob/main/files/jobs.csv": "jobs.csv"
}

upload_from_github("bkt-test-dev", github_files)
