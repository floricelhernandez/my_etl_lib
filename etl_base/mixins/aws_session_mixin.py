import os
from functools import cached_property

import boto3


class AwsSessionMixin:
    """Mixin simple para manejar sesión AWS, imprimir info y obtener clientes/recursos."""

    @cached_property
    def session(self):
        profile = os.getenv("AWS_PROFILE", "personal")
        region = os.getenv("AWS_REGION")
        if "AWS_EXECUTION_ENV" in os.environ:  # Glue u otro entorno AWS
            session = boto3.Session()
        else:
            session = boto3.Session(profile_name=profile, region_name=region)

        # Imprime info de STS automáticamente
        try:
            sts = session.client("sts")
            identity = sts.get_caller_identity()
            print(f"AWS Profile   : {profile}")
            print(f"AWS Region    : {session.region_name}")
            print(f"AWS Account ID: {identity.get('Account')}")
            print(f"AWS User ARN  : {identity.get('Arn')}")
        except Exception as e:
            print(f"No se pudo obtener info de STS: {e}")

        return session

    def get_client(self, service_name: str):
        """Devuelve un cliente boto3 con la sesión activa."""
        return self.session.client(service_name)

    def get_resource(self, service_name: str):
        """Devuelve un recurso boto3 con la sesión activa."""
        return self.session.resource(service_name)
