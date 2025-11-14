import os


class PathResolverMixin:
    """
    Provides utilities for resolving paths depending on the execution environment.
    """

    def resolve_path(self, relative_path: str) -> str:
        """
        Returns a fully qualified path depending on environment:
        - Local: ./data/relative_path
        - Glue: s3://my-bucket-name/relative_path
        """
        if self.storage == "s3":
            return f"s3://{self.storage_source}/{relative_path}"
        else:
            return os.path.join(self.storage_source, relative_path)
