import sys
import time
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F


# =========================================
# CONFIGURACIÓN DE JOB
# =========================================
if "--JOB_NAME" not in sys.argv:
    sys.argv += ["--JOB_NAME", "local_test"]

if "--storage_source" not in sys.argv:
    sys.argv += ["--storage_source", "default-bucket"]

args = getResolvedOptions(sys.argv, ["JOB_NAME", "storage_source"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

start_time = time.time()

# =========================================
# RUTAS DE ENTRADA Y SALIDA
# =========================================
S3_INPUT_PATH = f"s3://{args['storage_source']}/datasets/personas/"
S3_OUTPUT_PATH = f"s3://{args['storage_source']}/datasets_output/personas_agg_s3/"

print(f"\nLeyendo datos desde: {S3_INPUT_PATH}")
print(f"Guardando salida en: {S3_OUTPUT_PATH}\n")

# =========================================
# LECTURA CON OPTIMIZACIÓN
# =========================================
read_start = time.time()

glue_dynamic_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [S3_INPUT_PATH],
        "recurse": True,
        "groupFiles": "inPartition",
        "groupSize": "1048576",  # 1 MB, para prueba; en producción 64–256 MB
    },
    push_down_predicate="pais in ('Mexico','Chile')",  # aprovecha las particiones si estan en formato parquet, orc y glue data catalog

    format="csv",
    format_options={"withHeader": True}
)

df = glue_dynamic_frame.toDF()
read_end = time.time()

# =========================================
# MÉTRICAS DE LECTURA
# =========================================
input_files = df.inputFiles()
num_files = len(input_files)
num_partitions = df.rdd.getNumPartitions()
num_rows = df.count()



print("========== 📊 MÉTRICAS DE LECTURA ==========")
print(f"Archivos leídos: {num_files}")

print(f"Filas totales leídas: {num_rows}")
print(f"Particiones en memoria: {num_partitions}")
print(f"Tiempo de lectura: {read_end - read_start:.2f} s")
print("===========================================\n")

# =========================================
# TRANSFORMACIONES
# =========================================
transform_start = time.time()



df_result = (
    df.groupBy("pais")
    .agg(
        F.avg("edad").alias("edad_promedio"),
        F.count("*").alias("num_personas")
    )
)

transform_end = time.time()

# =========================================
# SALIDA OPTIMIZADA
# =========================================
write_start = time.time()

df_result.coalesce(4).write \
    .mode("overwrite") \
    .partitionBy("pais") \
    .option("compression", "snappy") \
    .parquet(S3_OUTPUT_PATH)

write_end = time.time()

# =========================================
# MÉTRICAS DE ESCRITURA
# =========================================
total_time = time.time() - start_time

print("========== MÉTRICAS DEL JOB ==========")
print(f"Tiempo total: {total_time:.2f} s")
print(f"Filas de salida: {df_result.count()}")
print(f"Transformación: {transform_end - transform_start:.2f} s")
print(f"Escritura: {write_end - write_start:.2f} s")
print("=====================================\n")

print(f"Datos procesados y guardados en {S3_OUTPUT_PATH}")

job.commit()
