from google.cloud import bigquery

# Inicializa el cliente con el proyecto activo
client = bigquery.Client(project="etl-gb-poc")

# ID completo de la tabla destino
table_id = "etl-gb-poc.hresources.departments"

# Filas de ejemplo a insertar
rows_to_insert = [
    {"department_name": "Finance"},
    {"department_name": "Human Resources 2"},
    {"department_name": "Engineering Data Department"},
]

# Inserción en BigQuery
errors = client.insert_rows_json(table_id, rows_to_insert)

if errors == []:
    print(f"inserted {len(rows_to_insert)} rows in {table_id}")
else:
    print("Errors while inserting:", errors)
