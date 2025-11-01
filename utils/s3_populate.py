import boto3
import pandas as pd
import random
import string
import io

# Parámetros configurables
BUCKET_NAME = "pechel-use1-lake"
BASE_PREFIX = "datasets/personas"
NUM_FILES = 50           # cantidad de archivos a generar
ROWS_PER_FILE = 5000     # filas por archivo
PAISES = ["Mexico", "Argentina", "Chile", "Colombia", "Peru", "España"]

# Inicializa cliente S3
s3 = boto3.client("s3")

# Función auxiliar para generar nombres aleatorios
def generar_nombre():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

# Generar y subir archivos particionados
for i in range(NUM_FILES):
    pais = random.choice(PAISES)
    data = {
        "id": range(i * ROWS_PER_FILE, (i + 1) * ROWS_PER_FILE),
        "nombre": [generar_nombre() for _ in range(ROWS_PER_FILE)],
        "edad": [random.randint(18, 70) for _ in range(ROWS_PER_FILE)],
        "pais": [pais] * ROWS_PER_FILE,
    }
    df = pd.DataFrame(data)

    # Convertir DataFrame a CSV en memoria
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Ruta particionada en S3
    key = f"{BASE_PREFIX}/pais={pais}/data_{i}.csv"

    # Subir a S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_buffer.getvalue(),
    )

    print(f"Subido: s3://{BUCKET_NAME}/{key}")

print("✅ Archivos generados y subidos correctamente.")
