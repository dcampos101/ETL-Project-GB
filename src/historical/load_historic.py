#Load ini program
import requests
import pandas as pd
import io
from google.cloud import storage

def try_read_csv(text, expected_cols):
    """Try reading the CSV file with different separators"""
    for sep in [",", ";", "\t", " "]:
        try:
            df = pd.read_csv(io.StringIO(text), header=None, sep=sep, engine="python", on_bad_lines="skip")
            if df.shape[1] == expected_cols:
                print(f"✔ Separator detected: '{sep}' ({expected_cols} columns)")
                return df
        except Exception as e:
            continue
    print(f"⚠ No separator could be detected with {expected_cols} columns")
    return None

def process_and_upload(bucket_name, github_files):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for url, config in github_files.items():
        print(f"\nProcessing file: {config['destination']}")

        # Download file from GitHub
        response = requests.get(url)
        response.raise_for_status()

        # Try reading with auto‑detection
        df = try_read_csv(response.text, len(config["headers"]))
        if df is None:
            continue

        # Assign headers
        df.columns = config["headers"]

        # Report missing values
        print("Missing values per column:")
        print(df.isnull().sum())

        # Save temporary file with header
        temp_file = f"temp_{config['destination']}"
        df.to_csv(temp_file, index=False)

        # Upload to GCS
        blob = bucket.blob(config["destination"])
        blob.upload_from_filename(temp_file)

        print(f"✅ File {config['destination']} uploaded to gs://{bucket_name}/{config['destination']}")

# Configuration of your files
github_files = {
    "https://raw.githubusercontent.com/dcampos101/ETL-Project-GB/refs/heads/main/files/departments.csv": {
        "headers": ["department_id", "department_name"],
        "destination": "departments.csv"
    },
    "https://raw.githubusercontent.com/dcampos101/ETL-Project-GB/refs/heads/main/files/jobs.csv": {
        "headers": ["job_id", "job_title"],
        "destination": "jobs.csv"
    },
    "https://raw.githubusercontent.com/dcampos101/ETL-Project-GB/refs/heads/main/files/hired_employees.csv": {
        "headers": ["employee_id", "name", "hire_date", "department_id", "job_id"],
        "destination": "hired_employees.csv"
    }
}

# Ejecutar carga
process_and_upload("bkt-historic-files", github_files)
