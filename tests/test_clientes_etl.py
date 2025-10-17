# tests/test_clientes_etl.py
import os
import unittest.mock

import pandas as pd
import pytest

from etl_base.mixins.path_resolver_mixin import PathResolverMixin
from etls.clientes_etl import ClientesETL



def test_clientes_etl_run(tmp_path):
    # Creamos el CSV de prueba
    csv_path = tmp_path / "bronze/clientes.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"nombre": ["Ana", "Luis"], "edad": [25, 30]}).to_csv(
        csv_path, index=False
    )

    # Argumentos que simularemos en CLI
    cli_args = [
        "program_name",  # sys.argv[0] normalmente
        "--env",
        "local",
        "--storage_source",
        str(tmp_path),
    ]

    arg_names = ["env", "storage_source"]

    # Usamos patch para reemplazar sys.argv temporalmente
    with unittest.mock.patch("sys.argv", cli_args):
        etl = ClientesETL(arg_names=arg_names)
        etl.run()

    # Verificamos que el parquet se generó
    parquet_path = tmp_path / "silver/clientes.parquet"
    assert parquet_path.exists()

    # Verificamos contenido
    df = pd.read_parquet(parquet_path)
    assert list(df.columns) == ["nombre", "edad"]
    assert df.shape[0] == 2


# Clase mínima para testear el mixin
class DummyETL(PathResolverMixin):
    def __init__(self, env, storage_source):
        self.env = env
        self.storage_source = storage_source


@pytest.mark.parametrize(
    "env, relative_file",
    [
        ("local", "clientes.csv"),
        ("local", "clientes2.csv"),
        ("glue", "clientes.csv"),
        ("glue", "clientes2.csv"),
    ],
)
def test_resolve_path(env, relative_file, tmp_path):
    # Para local usamos tmp_path como storage_source
    if env == "local":
        storage_source = str(tmp_path)
        expected = os.path.join(storage_source, relative_file)
    else:
        # Para glue simulamos bucket
        storage_source = "my-bucket"
        expected = f"s3://{storage_source}/{relative_file}"

    etl = DummyETL(env=env, storage_source=storage_source)
    result = etl.resolve_path(relative_file)

    assert result == expected
