import os

# ----------------------------------------------------
# Configuración
# ----------------------------------------------------
PROJECT_ROOT = os.getcwd()  # usar el directorio actual
PACKAGE_NAME = "etl_base"
MIXINS_DIR = os.path.join(PROJECT_ROOT, PACKAGE_NAME, "mixins")
ETLS_DIR = os.path.join(PROJECT_ROOT, "etls")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
BRONZE_DIR = os.path.join(DATA_DIR, "bronze")


# ----------------------------------------------------
# Función auxiliar para crear archivos y carpetas
# ----------------------------------------------------
def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Creado: {path}")


# ----------------------------------------------------
# Crear estructura de proyecto
# ----------------------------------------------------
def create_structure():
    # setup.py
    setup_content = """from setuptools import setup, find_packages

setup(
    name="etl_base",
    version="0.1.0",
    packages=find_packages(include=["etl_base", "etl_base.*"]),
    install_requires=[
        "boto3",
        "pandas",
        "pyarrow",
    ],
    python_requires=">=3.8",
)
"""
    create_file(os.path.join(PROJECT_ROOT, "setup.py"), setup_content)

    # requirements.txt
    requirements_content = "boto3\npandas\npyarrow\n"
    create_file(os.path.join(PROJECT_ROOT, "requirements.txt"), requirements_content)

    # README.md vacío
    create_file(os.path.join(PROJECT_ROOT, "README.md"))

    # etl_base package
    create_file(os.path.join(PROJECT_ROOT, PACKAGE_NAME, "__init__.py"))
    create_file(os.path.join(PROJECT_ROOT, PACKAGE_NAME, "base_etl.py"))

    # mixins
    create_file(os.path.join(MIXINS_DIR, "__init__.py"))
    create_file(os.path.join(MIXINS_DIR, "path_resolver_mixin.py"))
    create_file(os.path.join(MIXINS_DIR, "s3_read_mixin.py"))
    create_file(os.path.join(MIXINS_DIR, "s3_write_mixin.py"))

    # etls
    create_file(os.path.join(ETLS_DIR, "__init__.py"))
    create_file(os.path.join(ETLS_DIR, "clientes_etl.py"))
    create_file(os.path.join(ETLS_DIR, "pagos_etl.py"))

    # tests
    create_file(os.path.join(TESTS_DIR, "__init__.py"))
    create_file(os.path.join(TESTS_DIR, "test_clientes_etl.py"))
    create_file(os.path.join(TESTS_DIR, "test_pagos_etl.py"))

    # data folders
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(BRONZE_DIR, exist_ok=True)
    print(f"Creado: {RAW_DIR} y {BRONZE_DIR}")

    print("\nEstructura de proyecto creada en:", PROJECT_ROOT)


# ----------------------------------------------------
# Ejecutar
# ----------------------------------------------------
if __name__ == "__main__":
    create_structure()
