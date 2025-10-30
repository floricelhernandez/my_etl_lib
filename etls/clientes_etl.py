# etls/clientes_etl.py
from etl_base.base_etl import BaseETL
from etl_base.mixins.aws_session_mixin import AwsSessionMixin
from etl_base.mixins.s3_read_mixin import S3ReadMixin
from etl_base.mixins.s3_write_mixin import S3WriteMixin


class ClientesETL(BaseETL, S3ReadMixin, S3WriteMixin, AwsSessionMixin):
    def extract(self):

        return self.read_csv("bronze/clientes.csv")

    def transform(self, data):
        # TODO: Crear un mixin de transformaciones comunes
        data.columns = [c.strip().lower() for c in data.columns]
        return data

    def load(self, data):
        self.write_parquet(data, "silver/clientes.parquet")


if __name__ == "__main__":
    args = ["env", "storage", "storage_source"]

    etl = ClientesETL(args)
    etl.run()
