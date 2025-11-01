import sys
import time
import logging
from awsglue import DynamicFrame
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F

# =========================================
# CONFIGURACIÓN DE LOGGING
# =========================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

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
S3_OUTPUT_PATH = f"s3://{args['storage_source']}/datasets_output/personas_agg_s3_bookmarks/"

logger.info(f" Leyendo datos desde: {S3_INPUT_PATH}")
logger.info(f" Guardando salida en: {S3_OUTPUT_PATH}")

# =========================================
# LECTURA CON BOOKMARKS
# =========================================
read_start = time.time()

try:
    glue_dynamic_frame = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [S3_INPUT_PATH],
            "recurse": True,
            "groupFiles": "inPartition",
            "groupSize": "1048576",  # 1 MB
            "pushDownPredicate": "pais in ('Mexico','Chile')",
            "jobBookmarkKeys": ["pais"],
            "jobBookmarkKeysSortOrder": "asc"
        },
        format="csv",
        format_options={"withHeader": True},
        transformation_ctx="source_ctx"
    )
    df = glue_dynamic_frame.toDF()
except Exception as e:
    logger.error(f"Error durante la lectura: {e}", exc_info=True)
    raise

read_end = time.time()

# =========================================
# MÉTRICAS DE LECTURA
# =========================================
input_files = df.inputFiles()
num_files = len(input_files)
num_partitions = df.rdd.getNumPartitions()
num_rows = df.count()

logger.info("==========  MÉTRICAS DE LECTURA ==========")
logger.info(f" Archivos leídos: {num_files}")
logger.info(f" Filas totales leídas: {num_rows}")
logger.info(f" Particiones en memoria: {num_partitions}")
logger.info(f" Tiempo de lectura: {read_end - read_start:.2f} s")
logger.info("===========================================")

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
# SALIDA CON BOOKMARKS
# =========================================
write_start = time.time()

try:
    glueContext.write_dynamic_frame.from_options(
        frame=DynamicFrame.fromDF(df_result, glueContext, "result_dyf"),
        connection_type="s3",
        connection_options={
            "path": S3_OUTPUT_PATH,
            "partitionKeys": ["pais"]
        },
        format="parquet",
        format_options={"compression": "snappy"},
        transformation_ctx="sink_ctx"
    )
except Exception as e:
    logger.error(f"Error durante la escritura: {e}", exc_info=True)
    raise

write_end = time.time()

# =========================================
# MÉTRICAS DE ESCRITURA
# =========================================
total_time = time.time() - start_time
output_rows = df_result.count()

logger.info("========== 📈 MÉTRICAS DEL JOB ==========")
logger.info(f"Tiempo total: {total_time:.2f} s")
logger.info(f" Filas de salida: {output_rows}")
logger.info(f"Transformación: {transform_end - transform_start:.2f} s")
logger.info(f" Escritura: {write_end - write_start:.2f} s")
logger.info("=========================================")
logger.info(f"Datos procesados y guardados en {S3_OUTPUT_PATH}")

job.commit()
