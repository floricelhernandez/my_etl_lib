import os
from io import BytesIO

import boto3
import pandas as pd


class S3ReadMixin:
    """
    Mixin para leer DataFrames desde parquet o CSV,
    ya sea en local o en S3.
    Depende de `resolve_path` del PathResolverMixin.
    """

    def read_parquet(self, relative_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo Parquet desde local o S3.
        """
        path = self.resolve_path(relative_path)

        if path.startswith("s3://"):
            bucket, key = self._split_s3_path(path)
            obj = boto3.client("s3").get_object(Bucket=bucket, Key=key)
            return pd.read_parquet(BytesIO(obj["Body"].read()), **kwargs)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            return pd.read_parquet(path, **kwargs)

    def read_csv(self, relative_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo CSV desde local o S3.
        """
        path = self.resolve_path(relative_path)

        if path.startswith("s3://"):
            bucket, key = self._split_s3_path(path)
            obj = boto3.client("s3").get_object(Bucket=bucket, Key=key)
            return pd.read_csv(BytesIO(obj["Body"].read()), **kwargs)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            return pd.read_csv(path, **kwargs)

    # TODO DRY: Mover a un mixin o utils común si es necesario
    @staticmethod
    def _split_s3_path(s3_path: str):
        """
        Divide una ruta S3 en bucket y key.
        Ej: s3://my-bucket/path/to/file.csv -> ("my-bucket", "path/to/file.csv")
        """
        assert s3_path.startswith("s3://"), f"Path no válido de S3: {s3_path}"
        parts = s3_path.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key
