import os

import awswrangler as wr
import pandas as pd


class S3WriteMixin:
    """
    Mixin para escribir DataFrames a Parquet o CSV, local o S3 usando awswrangler.
    Depende de `resolve_path` del PathResolverMixin y de una sesión AWS.
    """

    def write_parquet(self, df: pd.DataFrame, relative_path: str, **kwargs):
        """
        Escribe un DataFrame en Parquet.
        - Local: crea carpetas automáticamente.
        - S3: usa awswrangler con sesión de boto3.
        """
        path = self.resolve_path(relative_path)

        if self.storage == "s3":
            wr.s3.to_parquet(df=df, path=path, boto3_session=self.session, **kwargs)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_parquet(path, index=False, **kwargs)

    def write_csv(self, df: pd.DataFrame, relative_path: str, **kwargs):
        """
        Escribe un DataFrame en CSV.
        - Local: crea carpetas automáticamente.
        - S3: usa awswrangler con sesión de boto3.
        """
        path = self.resolve_path(relative_path)

        if self.storage == "s3":
            wr.s3.to_csv(df=df, path=path, boto3_session=self.session, **kwargs)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_csv(path, index=False, **kwargs)
