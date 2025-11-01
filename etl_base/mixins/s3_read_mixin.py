import json
import os

import awswrangler as wr
import pandas as pd


class S3ReadMixin:
    """
    Mixin para leer DataFrames desde Parquet o CSV,
    ya sea en local o en S3 usando awswrangler.
    Depende de `resolve_path` del PathResolverMixin y de una sesión AWS.
    """

    def read_parquet(self, relative_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo Parquet desde local o S3 usando awswrangler.
        """
        path = self.resolve_path(relative_path)

        if self.storage == "s3":
            # wr.s3.read_parquet acepta session de boto3
            return wr.s3.read_parquet(path=path, boto3_session=self.session, **kwargs)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            return pd.read_parquet(path, **kwargs)

    def read_csv(self, relative_path: str, **kwargs) -> pd.DataFrame:
        """
        Lee un archivo CSV desde local o S3 usando awswrangler.
        """
        path = self.resolve_path(relative_path)

        if self.storage == "s3":
            return wr.s3.read_csv(path=path, boto3_session=self.session, **kwargs)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            return pd.read_csv(path, **kwargs)
    def s3_read_config_file(self, file_path: str, **kwargs) -> dict:
        """
        Lee un archivo JSON desde S3 usando awswrangler.
        """
        

        if file_path.startswith("s3://"):
            s3 = self.session.client("s3")
            obj = s3.get_object(Bucket=file_path.split("/")[2], Key="/".join(file_path.split("/")[3:]))
            return json.loads(obj['Body'].read().decode('utf-8'))
        else:

            with open(file_path, "r") as f:
                config = json.load(f)
            return config
