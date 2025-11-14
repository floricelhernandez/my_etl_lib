import argparse
from abc import ABC, abstractmethod
import json

from .mixins.path_resolver_mixin import PathResolverMixin
from .mixins.s3_read_mixin import S3ReadMixin


class BaseETL(PathResolverMixin, ABC):

    def __init__(self, arg_names=None):
        """
        arg_names: lista de nombres de atributos a crear
        """
        self.arg_names = arg_names or []

        parser = argparse.ArgumentParser(description=f"ETL {self.__class__.__name__}")

        # Creamos argumentos dinámicamente
        for name in self.arg_names:
            parser.add_argument(f"--{name}", required=True, help=f"Valor para {name}")

        # Parseamos sys.argv (o patch en tests)
        args = parser.parse_args()

        # Seteamos atributos dinámicamente
        for name, value in vars(args).items():
            setattr(self, name, value)
        self.config= self.s3_read_config_file(self.config_path)
    
 
        

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def transform(self, data):
        pass

    @abstractmethod
    def load(self, data):
        pass

    def run(self):
        data = self.extract()
        transformed = self.transform(data)
        self.load(transformed)
