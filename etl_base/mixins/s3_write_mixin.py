import os
from io import BytesIO

import boto3
import pandas as pd


class S3WriteMixin:
    """
    Mixin para escribir DataFrames a parquet local o S3.
    Depende de `resolve_path` del PathResolverMixin.
    """

    def write_parquet(self, df: pd.DataFrame, relative_path: str, **kwargs):
        """
        Escribe un DataFrame en parquet.
        - Local: crea carpetas automáticamente.
        - S3: usa boto3 para subir.
        """
        path = self.resolve_path(relative_path)

        if path.startswith("s3://"):
            bucket, key = self._split_s3_path(path)
            buffer = BytesIO()
            df.to_parquet(buffer, index=False, **kwargs)
            buffer.seek(0)
            boto3.client("s3").put_object(
                Bucket=bucket, Key=key, Body=buffer.getvalue()
            )
        else:
            # Crear carpeta padre si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_parquet(path, index=False, **kwargs)

    # TODO DRY: Mover a un mixin o utils común si es necesario
    @staticmethod
    def _split_s3_path(s3_path: str):
        """
        Divide una ruta S3 en bucket y key.
        Ej: s3://my-bucket/path/to/file.parquet -> ("my-bucket", "path/to/file.parquet")
        """
        assert s3_path.startswith("s3://"), f"Path no válido de S3: {s3_path}"
        parts = s3_path.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key
