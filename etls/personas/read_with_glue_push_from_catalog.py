import sys
import time
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
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

start_time = time.time()

# =========================================
# CONFIGURACIONES DE ENTRADA Y SALIDA
# =========================================
DATABASE_NAME = "mi_base"
TABLE_NAME = "personas"
S3_OUTPUT_PATH = f"s3://{args['storage_source']}/datasets_output/personas_agg_s3_catalog/"

print(f"\n Leyendo desde Glue Catalog: {DATABASE_NAME}.{TABLE_NAME}")
print(f"Guardando resultados en: {S3_OUTPUT_PATH}\n")

# =========================================
# LECTURA DESDE CATALOGO (CON BOOKMARK + PARTICIONES)
# =========================================
# Si tu tabla está particionada, puedes usar pushDownPredicate para limitar qué particiones leer.
read_start = time.time()

source_dyf = glue_context.create_dynamic_frame.from_catalog(
    database=DATABASE_NAME,
    table_name=TABLE_NAME,
    transformation_ctx="source_ctx",
    
        
    push_down_predicate="pais in ('Mexico','Chile')"  #  solo leerá esas particiones
    
)

df = source_dyf.toDF()

read_end = time.time()

# =========================================
# MÉTRICAS DE LECTURA
# =========================================
input_files = df.inputFiles()
num_files = len(input_files)
num_partitions = df.rdd.getNumPartitions()
num_rows = df.count()

print("==========  MÉTRICAS DE LECTURA ==========")
print(f"Archivos leídos: {num_files}")
print(f"Filas totales leídas: {num_rows}")
print(f"Particiones en memoria: {num_partitions}")
print(f"Tiempo de lectura: {read_end - read_start:.2f} s")
print("===========================================\n")

# =========================================
# TRANSFORMACIÓN DE DATOS
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
# ESCRITURA OPTIMIZADA (PARQUET + PARTICIONES + SNAPPY)
# =========================================
write_start = time.time()

df_result.coalesce(2).write \
    .mode("overwrite") \
    .partitionBy("pais") \
    .option("compression", "snappy") \
    .parquet(S3_OUTPUT_PATH)

write_end = time.time()

# =========================================
# MÉTRICAS DEL JOB
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
